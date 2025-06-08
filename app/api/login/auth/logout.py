from fastapi import Depends, Response, Request
from jose import jwt, JWTError
from sqlalchemy import (
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

from core.jwt.helpers import _utc_now
from models.refresh_token import RefreshToken
from utils.cookie.helpers import (
    _clear_auth_cookies,
)
from config import app_settings
from config.db import get_async_session

router = APIRouter()


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Logs out the user by revoking the refresh token and clearing authentication cookies.

    Args:
        request (Request): The HTTP request object containing cookies.
        response (Response): The HTTP response object to modify cookies.
        session (AsyncSession): The database session dependency.

    Returns:
        dict: A response indicating the logout status.
    """
    refresh_cookie = request.cookies.get("refreshToken")
    if refresh_cookie:
        try:
            data = jwt.decode(
                refresh_cookie,
                app_settings.auth_jwt_public_key,
                algorithms=[app_settings.auth_jwt_algorithm],
            )
            jti = data.get("jti")
            if jti:
                await session.execute(
                    update(RefreshToken)
                    .where(RefreshToken.jti == jti)
                    .values(revoked_at=_utc_now())
                )
                await session.commit()
        except JWTError:
            pass
    _clear_auth_cookies(response)
    return {"detail": "ok"}
