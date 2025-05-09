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


router = APIRouter()


@router.get("/refresh")
async def login_refresh(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    refresh_cookie = request.cookies.get("refreshToken")
    if not refresh_cookie:
        raise HTTPException(401, "Missing refresh token")

    print("🍪 raw Cookie header:", request.headers.get("cookie"))

    try:
        data = jwt.decode(
            refresh_cookie,
            app_settings.jwt_public_key,
            algorithms=[app_settings.jwt_algorithm],
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
