from fastapi import Depends, HTTPException, Response, Body
from passlib.hash import argon2
from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

from core.jwt.helpers import issue_access_token, issue_refresh_token
from models.user import User
from schemas.login import LoginPasswordRequest, LoginPasswordResponse
from utils.cookie.helpers import (
    _set_auth_cookies,
)
from config.db import get_async_session
from typing import Annotated

router = APIRouter()


@router.post(
    "/password",
    summary="Аутентификация с паролем",
    description="Принимает email и пароль пользователя. В случае успеха возвращает 200 код и устанавливает куку `accessToken` и `refreshToken`.",
    response_model=LoginPasswordResponse
)
async def login_password(
    req: Annotated[LoginPasswordRequest, Body()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    response: Response,
):
    """
    Authenticate a user using email and password.

    Args:
        req (LoginPasswordRequest): The login request containing email, password, and organization ID.
        response (Response): The HTTP response object to set cookies.
        session (AsyncSession): The database session dependency.

    Returns:
        dict: A dictionary containing the access and refresh tokens.
        The access token is set in the "accessToken" cookie, and the refresh token is set in the "refreshToken" cookie.
        The tokens are used for authentication in subsequent requests.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    res = await session.execute(
        select(User).where(
            User.email == req.email, User.organization_id == req.organization_id
        )
    )
    user: User | None = res.scalar_one_or_none()
    if not user or not argon2.verify(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Bad credentials")

    access = issue_access_token(user)
    refresh = issue_refresh_token(user, session)
    await session.commit()

    _set_auth_cookies(response, access, refresh)
    return LoginPasswordResponse(accessToken=access, refreshToken=refresh)
