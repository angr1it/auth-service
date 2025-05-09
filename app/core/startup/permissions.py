from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Resource, Permission
from core.permission.registry import BUILTIN_PERMISSIONS


async def ensure_base_permissions(db: AsyncSession):
    for resource_name, codes in BUILTIN_PERMISSIONS.items():
        resource_result = await db.execute(
            select(Resource).where(Resource.name == resource_name)
        )
        resource = resource_result.scalar_one_or_none()

        if not resource:
            resource = Resource(name=resource_name)
            db.add(resource)
            await db.flush()

        for code in codes:
            perm_result = await db.execute(
                select(Permission).where(
                    Permission.resource_id == resource.id,
                    Permission.code == code,
                )
            )
            perm = perm_result.scalar_one_or_none()
            if not perm:
                db.add(Permission(resource_id=resource.id, code=code))

    await db.commit()