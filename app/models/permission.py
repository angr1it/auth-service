"""
Модель для разрешений.

Classes:
    Permission: Модель разрешения, связанного с ресурсом.
"""

from __future__ import annotations
import datetime

from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Permission(Base):
    """
    Модель разрешения.

    Attributes:
        id (int): Уникальный идентификатор разрешения.
        resource_id (int): ID ресурса, к которому относится разрешение.
        code (str): Код разрешения.
        description (str | None): Описание разрешения.
        resource (Resource): Связанный ресурс.
        users (list[UserPermission]): Список пользователей, имеющих это разрешение.
        added_at (datetime): Дата и время создания записи.
    """

    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    code: Mapped[str] = mapped_column(String, unique=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    resource: Mapped["Resource"] = relationship(back_populates="permissions")

    users: Mapped[list["UserPermission"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("resource_id", "code", name="uq_resource_code"),)

    added_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
