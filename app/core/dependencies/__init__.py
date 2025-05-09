from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from core.permission.helpers import fetch_permissions
from schemas.token import TokenMeta
from utils.helpers.jwt import decode_jwt
from config.db import get_async_session
from core.permission.registry import OrganizationPermissions, BuiltinResource


bearer_scheme = HTTPBearer(auto_error=False)


async def token_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials:
        return credentials.credentials
    cookie = request.cookies.get("accessToken")
    if cookie:
        return cookie
    raise HTTPException(401, "Missing access token")


def payload_from_request(
    token: Annotated[str, Depends(token_from_request)],
) -> TokenMeta:
    return TokenMeta(**decode_jwt(token))


async def ensure_owner(
    payload: Annotated[TokenMeta, Depends(payload_from_request)],
    sess: AsyncSession = Depends(get_async_session),
) -> TokenMeta:
    perms = await fetch_permissions(sess, payload.sub)

    if not BuiltinResource.organization in perms:
        raise HTTPException(403, "Permission denied")
    if not OrganizationPermissions.owner in perms[BuiltinResource.organization]:
        raise HTTPException(403, "Permission denied")

    return payload
