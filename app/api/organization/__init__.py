from fastapi import APIRouter

from api.organization.create import router as create_router
from api.organization.invite import router as invite_router
from api.organization.register import router as register_router
from api.organization.user import router as user_router

organization_router = APIRouter()

organization_router.include_router(create_router, tags=["create"])
organization_router.include_router(invite_router, tags=["invite"])
organization_router.include_router(register_router, tags=["register"])
organization_router.include_router(user_router, tags=["user"])
