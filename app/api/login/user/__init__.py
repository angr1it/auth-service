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


@router.get(
    "/user",
    summary="Предоставляет обобщённую информацию о текущем пользователе",
    description="Предоставляет обобщённую информацию о текущем пользователе, включая email, ID, аватар, наименование организации и права доступа по ресурсам. Используется клиентом для определения интерфейса, доступного пользователю.",
    response_model=UserOutput,
    responses={
        404: {"description": "User not found"},
        401: {"description": "Permissions changed; re‑authenticate"},
    }
    
)
async def current_user(
    token: Annotated[str, Depends(token_from_request)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Retrieve the current authenticated user and their permissions.

    Args:
        token (str): The access token extracted from the request.
        session (AsyncSession): The database session dependency.

    Returns:
        UserOutput: The authenticated user's details, including permissions.

    Raises:
        HTTPException: If the user is not found, their permissions have changed, or validation fails.

    Notes:
        - The access token is decoded to extract the user ID (`sub`) and organization ID (`org`).
        - The user and their organization are validated against the database.
        - If the user's permission version (`perm_version`) does not match the token's version, re-authentication is required.
        - The user's permissions are fetched and included in the response.
        - Validation ensures the user exists, belongs to the correct organization, and has up-to-date permissions.
    """
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
