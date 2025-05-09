from fastapi import Response

from config import app_settings


def _set_access_cookie(response: Response, access: str):
    response.set_cookie(
        "accessToken",
        access,
        max_age=int(app_settings.access_token_ttl.total_seconds()),
        httponly=True,
        secure=True,
        samesite="lax",
        domain=app_settings.cookie_domain,
        path="/"
    )


def _set_refresh_cookie(response: Response, refresh: str):
    response.set_cookie(
        "refreshToken",
        refresh,
        max_age=int(app_settings.refresh_token_ttl.total_seconds()),
        httponly=True,
        secure=True,
        samesite="lax",
        domain=app_settings.cookie_domain,
        path="/"
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie("accessToken", domain=app_settings.cookie_domain, path="/")
    response.delete_cookie(
        "refreshToken", domain=app_settings.cookie_domain, path="/login"
    )


def _set_auth_cookies(response: Response, access: str, refresh: str):
    _set_access_cookie(response, access)
    _set_refresh_cookie(response, refresh)
