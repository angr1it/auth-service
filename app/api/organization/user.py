from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.permission import PermissionEdit
from core.organization import get_users_by_organization
from schemas import PaginationModel
from core.dependencies import ensure_owner
from schemas.token import TokenMeta
from config.db import get_async_session
from schemas.user import UserOutput, PaginatedUsers
from core.permission.helpers import fetch_permissions, add_permissions_to_user


router = APIRouter()


@router.post("/users", response_model=PaginatedUsers)
async def get_users(
    req: PaginationModel,
    payload: Annotated[TokenMeta, Depends(ensure_owner)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Получает список пользователей для указанной организации.

    Args:
        req (PaginationModel): Параметры пагинации (offset, limit, page, size).
        payload (TokenMeta): Токен с информацией о пользователе и организации.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        PaginatedUsers: Объект, содержащий список пользователей, общее количество,
        текущую страницу, размер страницы и общее количество страниц.
    """
    users, total = await get_users_by_organization(
        session=session, organization_id=payload.org, offset=req.offset, limit=req.limit
    )

    return PaginatedUsers(
        items=[
            UserOutput(
                id=user.id,
                email=user.email,
                login=user.login,
                avatar_url=user.avatar_url,
                permissions=await fetch_permissions(session, user.id),
                perm_version=user.perm_version,
                operator_id=user.operator_id,
            )
            for user in users
        ],
        total=total,
        page=req.page,
        size=req.size,
        pages=total // req.size + (total % req.size > 0),
    )


@router.post("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: int,
    req: PermissionEdit,
    _: Annotated[TokenMeta, Depends(ensure_owner)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет права доступа пользователя.

    Args:
        user_id (int): ID пользователя, чьи права нужно обновить.
        req (PermissionEdit): Объект с новыми правами доступа.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если переданы некорректные права доступа.

    Returns:
        200 OK: Если права доступа успешно обновлены.
        400 Bad Request: Если переданы некорректные права доступа.
    """
    try:
        await add_permissions_to_user(
            db=session,
            user_id=user_id,
            permissions_dict=req.permissions,
            ignore_invalid=False,
            upsert=False,
            commit=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
