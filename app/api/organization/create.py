from fastapi import Depends, HTTPException, APIRouter
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from config.db import get_async_session
from models.organization import Organization
from schemas.organization import OrganizationCreateRequest
from core.permission.helpers import add_owner_permission_to_user

router = APIRouter()


@router.post("/create")
async def create_org(
    req: OrganizationCreateRequest,
    session: AsyncSession = Depends(get_async_session),
):
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
    return {"organizationId": org_id}
