from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import app_settings


engine = create_async_engine(
    url=str(app_settings.database_dsn),
    echo=app_settings.echo_db_engine,
    pool_pre_ping=True,
)

db_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_session() as session:
        yield session


@asynccontextmanager
async def commit_on_success(db: AsyncSession):
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    else:
        await db.commit()
