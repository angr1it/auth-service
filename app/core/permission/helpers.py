from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import UserPermission
from models.permission import Permission
from models.resource import Resource
from schemas.permission import PermissionResponse
from core.permission.registry import BuiltinResource, OrganizationPermissions


async def add_permissions_to_user(
    db: AsyncSession,
    user_id: int,
    permissions_dict: dict[str, list[str]],
    ignore_invalid: bool = True,
    commit: bool = False,
    upsert: bool = True,
):
    """
    Добавляет разрешения пользователю.

    Args:
        db (AsyncSession): Активная сессия базы данных.
        user_id (int): ID пользователя.
        permissions_dict (dict[str, list[str]]): Словарь разрешений в формате {resource_name: [permission_code, ...]}.
        ignore_invalid (bool): Если True, игнорирует несуществующие ресурсы или разрешения. Если False, выбрасывает исключение.
        commit (bool): Если True, изменения будут зафиксированы в базе данных.
        upsert (bool): Если True, добавляет разрешения из permissions_dict, сохраняя существующие.
                       Если False, удаляет все текущие разрешения пользователя и заменяет их на permissions_dict.

    Raises:
        ValueError: Если ресурс или разрешение не найдены и ignore_invalid=False.
    """
    if not upsert:
        stmt = (
            select(UserPermission)
            .join(Permission, UserPermission.permission_id == Permission.id)
            .join(Resource, Permission.resource_id == Resource.id)
            .where(UserPermission.user_id == user_id)
        )
        result = await db.execute(stmt)
        current_permissions = result.scalars().all()

        allowed_permissions = {
            (resource_name, code)
            for resource_name, codes in permissions_dict.items()
            for code in codes
        }
        for user_permission in current_permissions:
            resource_name = user_permission.permission.resource.name
            code = user_permission.permission.code
            if (resource_name, code) not in allowed_permissions:
                await db.delete(user_permission)

    for resource_name, codes in permissions_dict.items():
        resource_result = await db.execute(
            select(Resource).where(Resource.name == resource_name)
        )
        resource = resource_result.scalar_one_or_none()

        if not resource:
            if ignore_invalid:
                continue
            raise ValueError(f"Resource '{resource_name}' not found")

        for code in codes:
            permission_result = await db.execute(
                select(Permission).where(
                    Permission.resource_id == resource.id, Permission.code == code
                )
            )
            permission = permission_result.scalar_one_or_none()

            if not permission:
                if ignore_invalid:
                    continue
                raise ValueError(
                    f"Permission '{code}' not found for resource '{resource_name}'"
                )

            existing_result = await db.execute(
                select(UserPermission).where(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_id == permission.id,
                )
            )
            exists = existing_result.scalar_one_or_none()

            if not exists:
                db.add(UserPermission(user_id=user_id, permission_id=permission.id))

    if commit:
        await db.commit()


async def fetch_permissions(db: AsyncSession, user_id: int) -> PermissionResponse:
    """
    Возвращает все разрешения пользователя в виде словаря: {resource_name: [permission_code, ...]}.

    Args:
        db (AsyncSession): Активная сессия базы данных
        user_id (int): Пользователь, для которого требуется получить разрешения

    Returns:
        словарь разрешений по ресурсам
    """

    stmt = (
        select(Permission.code, Resource.name)
        .join(Resource, Permission.resource_id == Resource.id)
        .join(UserPermission, UserPermission.permission_id == Permission.id)
        .where(UserPermission.user_id == user_id)
    )
    result = await db.execute(stmt)

    grouped: dict[str, list[str]] = defaultdict(list)
    for code, resource_name in result.all():
        grouped[resource_name].append(code)

    return dict(grouped)


async def add_owner_permission_to_user(
    db: AsyncSession, user_id: int, commit: bool = False
):
    """
    Добавляет разрешение 'owner' для ресурса 'organization' указанному пользователю.

    Args:
        db (AsyncSession): Активная сессия базы данных.
        user_id (int): ID пользователя.
        commit (bool): Если True, изменения будут зафиксированы в базе данных.
    """
    permissions_dict = {
        BuiltinResource.organization.value: [OrganizationPermissions.owner.value]
    }
    await add_permissions_to_user(
        db=db,
        user_id=user_id,
        permissions_dict=permissions_dict,
        ignore_invalid=False,
        commit=commit,
    )
