from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, Path
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


@router.post(
    "/users",
    summary="Возвращает список пользователей организации.",
    description="Возвращается список пользователей с их данными, а также общее количество пользователей, общее число страниц и текущий номер страницы для пагинации.",
    response_model=PaginatedUsers
)
async def get_users(
    req: Annotated[PaginationModel, Body()],
    payload: Annotated[TokenMeta, Depends(ensure_owner)],
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieve a list of users for the specified organization.

    Args:
        req (PaginationModel): Pagination parameters (offset, limit, page, size).
        payload (TokenMeta): Token containing user and organization information.
        session (AsyncSession): The database session dependency.

    Returns:
        PaginatedUsers: A paginated list of users with their details and permissions.

    Notes:
        - The token is validated to ensure the user is an owner of the organization.
        - Validation ensures the user exists and has the necessary permissions.
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


@router.post(
    "/users/{user_id}/permissions",
    summary="Обновление разрешений пользователя.",
    description="Обновление разрешений у переданного пользователя.",
    responses={
        400: {"description": "Текст исключения"}
    }
)
async def update_user_permissions(
    user_id: Annotated[int, Path()],
    req: Annotated[PermissionEdit, Body()],
    _: Annotated[TokenMeta, Depends(ensure_owner)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Update the permissions of a specific user.

    Args:
        user_id (int): The ID of the user whose permissions need to be updated.
        req (PermissionEdit): Object containing the new permissions.
        session (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If invalid permissions are provided.

    Returns:
        200 OK: If permissions are successfully updated.
        400 Bad Request: If invalid permissions are provided.

    Notes:
        - The token is validated to ensure the user is an owner of the organization.
        - Validation ensures the user exists and belongs to the correct organization.
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
