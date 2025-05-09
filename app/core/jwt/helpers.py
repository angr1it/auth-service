import datetime as dt
from uuid import uuid4

from fastapi import (
    HTTPException,
    status,
)
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from schemas.token import JwtPayload
from models import RefreshToken, User
from config import app_settings


def _utc_now() -> dt.datetime:
    return dt.datetime.now(tz=dt.timezone.utc)


def issue_access_token(user: User) -> str:
    """Create signed JWT with minimal claims."""
    now = _utc_now()
    payload = {
        "sub": str(user.id),
        "org": user.organization_id,
        "login": user.login,
        "iat": int(now.timestamp()),
        "exp": int((now + app_settings.access_token_ttl).timestamp()),
        "jti": uuid4().hex,
        "pv": user.perm_version,
    }
    return jwt.encode(
        payload, app_settings.jwt_private_key, algorithm=app_settings.jwt_algorithm
    )


def issue_refresh_token(user: User, session: AsyncSession) -> str:
    now = _utc_now()
    jti = uuid4().hex
    exp = now + app_settings.refresh_token_ttl

    payload = {
        "sub": str(user.id),
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(
        payload, app_settings.jwt_private_key, algorithm=app_settings.jwt_algorithm
    )
    rt = RefreshToken(
        jti=jti, user_id=user.id, expires_at=exp
    )
    session.add(rt)
    return token


def decode_access_token(token: str) -> JwtPayload:
    try:
        data = jwt.decode(
            token, app_settings.jwt_public_key, algorithms=[app_settings.jwt_algorithm]
        )
        return JwtPayload(**data)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc


