from fastapi import Depends, HTTPException, APIRouter, Body
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from config.db import get_async_session
from models.organization import Organization
from schemas.organization import OrganizationCreateRequest, OrganizationCreateResponse
from core.permission.helpers import add_owner_permission_to_user
from typing import Annotated
router = APIRouter()


@router.post(
    "/create",
    summary="Создание организации и владельца.",
    description="Возвращает id созданной организации",
    response_model=OrganizationCreateResponse,
    responses={
        400: {"description": "organization slug already exists. login already exists"}
    }
)
async def create_org(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    req: Annotated[OrganizationCreateRequest, Body()]
):
    """
    Create a new organization and its owner.

    Args:
        req (OrganizationCreateRequest): The request containing organization and owner details.
        session (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If the organization slug or owner login already exists.

    Returns:
        dict: The ID of the newly created organization.

    Notes:
        - Validation ensures the organization slug is unique.
        - Validation ensures the owner login is unique.
    """
    if not req.organization_slug:
        req.organization_slug = req.organization_name.lower().replace(" ", "-")[:64]

    exists = await session.get(Organization, req.organization_slug)
    if exists:
        raise HTTPException(400, "organization slug already exists")

    org = Organization(id=req.organization_slug, name=req.organization_name)

    user_exists = await session.execute(select(User).where(User.login == req.login))
    user_exists = user_exists.scalars().first()

    if user_exists:
        raise HTTPException(400, "login already exists")

    owner = User(
        organization_id=req.organization_slug,
        email=req.email,
        login=req.login,
        password_hash=argon2.hash(req.password),
        perm_version=1,
        operator_id=req.operator_id,
    )
    session.add_all([org, owner])
    await session.flush()
    await add_owner_permission_to_user(
        db=session,
        user_id=owner.id,
        commit=False,
    )
    org_id = org.id
    await session.commit()
    return OrganizationCreateResponse(organizationId=org_id)
