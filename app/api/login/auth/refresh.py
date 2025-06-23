from fastapi import Depends, HTTPException, Response, Request, APIRouter
from jose import jwt, JWTError

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.jwt.helpers import _utc_now, issue_access_token
from models.refresh_token import RefreshToken
from models.user import User
from utils.cookie.helpers import (
    _set_access_cookie,
)
from config.db import get_async_session
from config import app_settings
from typing import Annotated

router = APIRouter()


@router.get(
    "/refresh",
    summary="Обновление accessToken",
    description="Обновляет accessToken, если refreshToken валидный.",
    responses={
        401: {"description": "Missing refresh token. Invalid refresh token. Malformed refresh token. Refresh token revoked or expired"}
    }
)
async def login_refresh(
    response: Response,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Refresh the access token using a valid refresh token.

    Args:
        response (Response): The HTTP response object to set the updated access token cookie.
        request (Request): The HTTP request object containing the refresh token cookie.
        session (AsyncSession): The database session dependency.

    Returns:
        None: The updated access token is set in the "accessToken" cookie.

    Raises:
        HTTPException: If the refresh token is missing, invalid, expired, revoked, or malformed.

    Notes:
        - The "accessToken" cookie is updated with a new access token upon successful validation of the refresh token.
        - The refresh token is validated against the database to ensure it has not been revoked or expired.
    """
    refresh_cookie = request.cookies.get("refreshToken")
    if not refresh_cookie:
        raise HTTPException(401, "Missing refresh token")

    print("🍪 raw Cookie header:", request.headers.get("cookie"))

    try:
        data = jwt.decode(
            refresh_cookie,
            app_settings.auth_jwt_public_key,
            algorithms=[app_settings.auth_jwt_algorithm],
        )
    except JWTError as e:
        print("JWTError:", str(e))
        raise HTTPException(401, "Invalid refresh token")

    jti = data.get("jti")
    user_id = int(data.get("sub"))
    exp_ts = data.get("exp")
    if not jti or not user_id:
        raise HTTPException(401, "Malformed refresh token")

    res = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt: RefreshToken | None = res.scalar_one_or_none()
    if not rt or rt.revoked_at is not None or rt.expires_at < _utc_now():
        raise HTTPException(401, "Refresh token revoked or expired")

    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
    access = issue_access_token(user)
    _set_access_cookie(response, access)
