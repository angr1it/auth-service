from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import token_from_request
from core.jwt.helpers import decode_access_token
from core.permission.helpers import fetch_permissions
from models.organization import Organization
from models.user import User
from schemas.user import UserOutput
from config.db import get_async_session


router = APIRouter()


@router.get("/user", response_model=UserOutput)
async def current_user(
    token: Annotated[str, Depends(token_from_request)],
    session: AsyncSession = Depends(get_async_session),
):
    payload = decode_access_token(token)
    user_row = await session.execute(
        select(User, Organization)
        .join(Organization, User.organization_id == Organization.id)
        .where(User.id == int(payload.sub), Organization.id == payload.org)
    )
    row = user_row.first()
    if not row:
        raise HTTPException(404, "User not found")
    user: User = row[0]
    org: Organization = row[1]

    if user.perm_version != payload.pv:  # TODO:
        raise HTTPException(401, "Permissions changed; re‑authenticate")

    permissions = await fetch_permissions(session, user.id)

    return UserOutput(
        id=user.id,
        email=user.email,
        login=user.login,
        avatarUrl=user.avatar_url,
        permissions=permissions,
        perm_version=user.perm_version,
        operator_id=user.operator_id,
    )
