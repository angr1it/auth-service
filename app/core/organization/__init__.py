from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def get_users_by_organization(
    session: AsyncSession,
    organization_id: str,
    offset: int = 0,
    limit: int = 10,
) -> tuple[list[User], int]:
    """
    Асинхронно получает пользователей по организации с пагинацией.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        organization_id (str): ID организации для фильтрации пользователей.
        offset (int): Смещение для пагинации (по умолчанию 0).
        limit (int): Лимит записей для пагинации (по умолчанию 10).

    Returns:
        tuple[list[User], int]: Кортеж, содержащий:
            - list[User]: Список пользователей на текущей странице.
            - int: Общее количество пользователей в организации.
    """

    total_stmt = (
        select(func.count())
        .select_from(User)
        .where(User.organization_id == organization_id)
    )
    total = (await session.execute(total_stmt)).scalar_one()

    stmt = (
        select(User)
        .where(User.organization_id == organization_id)
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    items: list[User] = result.scalars().all()

    return items, total
