import datetime as dt

from fastapi import HTTPException, Response
from jose import jwt, JWTError

from config import app_settings

utcnow = lambda: dt.datetime.now(dt.timezone.utc)


def sign_jwt(payload: dict) -> str:
    return jwt.encode(
        payload, app_settings.jwt_private_key, algorithm=app_settings.jwt_algorithm
    )


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token, app_settings.jwt_public_key, algorithms=[app_settings.jwt_algorithm]
        )
    except JWTError:
        raise HTTPException(401, "Invalid token")


def set_cookie(resp: Response, name: str, value: str, max_age: int, path: str = "/"):
    resp.set_cookie(
        name,
        value,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="lax",
        domain=app_settings.cookie_domain,
        path=path,
    )


def clear_auth(resp: Response):
    resp.delete_cookie("accessToken", domain=app_settings.cookie_domain, path="/")
    resp.delete_cookie("refreshToken", domain=app_settings.cookie_domain, path="/login")
