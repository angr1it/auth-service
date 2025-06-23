from datetime import datetime as dt
from datetime import timezone, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import ensure_owner
from models.registration_token import RegistrationToken
from schemas.invite import InviteRequest, InviteResponse
from schemas.token import TokenMeta
from config.db import get_async_session
from utils.helpers.jwt import sign_jwt
from config import app_settings

router = APIRouter()


@router.post(
    "/invite",
    summary="Генерация токен-инвайта.",
    description="Генерация токен-инвайта для нового владельца. Возвращает токен и url с токеном",
    response_model=InviteResponse
)
async def invite_user(
    payload: Annotated[TokenMeta, Depends(ensure_owner)],
    sess: Annotated[AsyncSession, Depends(get_async_session)],
    body: Annotated[InviteRequest, Body()]
):
    """
    Generate an invite token for a new user.

    Args:
        body (InviteRequest): The invite request containing operator ID and expiration details.
        payload (TokenMeta): Token containing user and organization information.
        sess (AsyncSession): The database session dependency.

    Returns:
        dict: The invite token and its corresponding URL.

    Notes:
        - The token is validated to ensure the user is an owner of the organization.
        - Validation ensures the user exists and has the necessary permissions.
    """

    now = dt.now(timezone.utc)
    jti = uuid4().hex
    exp = now + timedelta(hours=body.expires_in_hours)
    token = sign_jwt(
        {
            "jti": jti,
            "org": payload.org,
            "typ": "invite",
            "op": body.operator_id,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }
    )
    sess.add(
        RegistrationToken(
            jti=jti,
            organization_id=payload.org,
            created_by=payload.sub,
            expires_at=exp,
            operator_id=body.operator_id,
        )
    )

    await sess.commit()
    return InviteResponse(inviteToken=token, url=f"{app_settings.registration_token_url_prefix}/{token}")
