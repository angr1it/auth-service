from datetime import datetime as dt
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.registration_token import RegistrationToken
from models.user import User
from schemas.register import RegisterRequest, RegisterResponse
from utils.helpers.jwt import decode_jwt
from config.db import get_async_session
from passlib.hash import argon2
from typing import Annotated

router = APIRouter()


@router.post(
    "/register/{invite_token}",
    summary="Регистрация по токену‑инвайту.",
    description="Регистрирует нового пользователя используя токен-инвайт. Возвращает id пользователя",
    response_model=RegisterResponse,
    responses={
        400: {"description": "Invite expired. Already used. Login already in use. Email or operator_id already in use within the organization"}
    }
)
async def register(
    invite_token: Annotated[str, Path()],
    req: Annotated[RegisterRequest, Body()],
    sess: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Register a new user using an invite token.

    Args:
        invite_token (str): The invite token for registration.
        req (RegisterRequest): The registration request containing user details.
        sess (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If the invite token is invalid, expired, or already used.
        HTTPException: If the login, email, or operator ID is already in use.

    Returns:
        dict: The ID of the newly registered user.

    Notes:
        - The invite token is decoded and validated for type, expiration, and usage.
        - Validation ensures the login, email, and operator ID are unique within the organization.
    """

    data = decode_jwt(invite_token)
    if data.get("typ") != "invite":
        raise HTTPException(400)
    if dt.fromtimestamp(data["exp"], timezone.utc) < dt.now(timezone.utc):
        raise HTTPException(400, "Invite expired")
    used = await sess.get(RegistrationToken, data["jti"])
    if not used or used.used_at:
        raise HTTPException(400, "Already used")

    existing_user = await sess.execute(select(User).filter_by(login=req.login))
    if existing_user.scalar():
        raise HTTPException(400, "Login already in use")

    conflicting_user = await sess.execute(
        select(User).filter(
            User.organization_id == data["org"],
            (User.email == req.email)
            | ((User.operator_id == data.get("op")) & (data.get("op") is not None)),
        )
    )
    if conflicting_user.scalar():
        raise HTTPException(
            400, "Email or operator_id already in use within the organization"
        )

    user = User(
        organization_id=data["org"],
        email=req.email,
        login=req.login,
        password_hash=argon2.hash(req.password),
        operator_id=data.get("op"),
    )
    sess.add(user)
    await sess.flush()
    used.used_at = dt.now(timezone.utc)
    user_id = user.id
    await sess.commit()
    return RegisterResponse(id=user_id)
