"""
Модель для ресурсов.

Classes:
    Resource: Модель ресурса, связанного с разрешениями.
"""

from __future__ import annotations
import datetime

from sqlalchemy import (
    TIMESTAMP,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Resource(Base):
    """
    Модель ресурса.

    Attributes:
        id (int): Уникальный идентификатор ресурса.
        name (str): Имя ресурса.
        description (str | None): Описание ресурса.
        permissions (list[Permission]): Список разрешений, связанных с ресурсом.
        added_at (datetime): Дата и время создания записи.
    """
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="resource", cascade="all, delete-orphan"
    )

    added_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )