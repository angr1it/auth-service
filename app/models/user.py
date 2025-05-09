"""
Модели для пользователей и их разрешений.

Classes:
    User: Модель пользователя.
    UserPermission: Модель связи между пользователями и разрешениями.
"""

from __future__ import annotations
import datetime

from sqlalchemy import (
    TIMESTAMP,
    Index,
    String,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.organization import Organization


class User(Base):
    """
    Модель пользователя.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        organization_id (str): ID организации, к которой принадлежит пользователь.
        email (str): Электронная почта пользователя.
        login (str): Логин пользователя.
        password_hash (str): Хэш пароля пользователя.
        perm_version (int): Версия разрешений пользователя.
        avatar_url (str | None): URL аватара пользователя.
        permissions (list[UserPermission]): Список разрешений пользователя.
        organization (Organization): Организация пользователя.
        refresh_tokens (list[RefreshToken]): Список токенов обновления пользователя.
        created_registration_tokens (list[RegistrationToken]): Список созданных регистрационных токенов.
        added_at (datetime): Дата и время создания записи.
        updated_at (datetime): Дата и время последнего обновления записи.
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))

    email: Mapped[str] = mapped_column(String, unique=False)
    login: Mapped[str] = mapped_column(String, unique=True)

    password_hash: Mapped[str] = mapped_column(String)
    perm_version: Mapped[int] = mapped_column(default=1)
    avatar_url: Mapped[str | None] = mapped_column(String)

    operator_id: Mapped[int] = mapped_column(nullable=True)

    permissions: Mapped[list["UserPermission"]] = relationship(back_populates="user")
    organization: Mapped["Organization"] = relationship(back_populates="users")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    created_registration_tokens: Mapped[list["RegistrationToken"]] = relationship(
        back_populates="creator"
    )

    added_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_org_email"),
        Index(
            "uq_org_operator_id",
            "organization_id", "operator_id",
            unique=True,
            postgresql_where=text("operator_id IS NOT NULL"),
        ),
    )

class UserPermission(Base):
    """
    Модель связи между пользователями и разрешениями.

    Attributes:
        id (int): Уникальный идентификатор записи.
        user_id (int): ID пользователя.
        permission_id (int): ID разрешения.
        user (User): Связанный пользователь.
        permission (Permission): Связанное разрешение.
        added_at (datetime): Дата и время создания записи.
        updated_at (datetime): Дата и время последнего обновления записи.
    """

    __tablename__ = "user_permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"))

    user: Mapped["User"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="users")

    added_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_perm"),
    )
