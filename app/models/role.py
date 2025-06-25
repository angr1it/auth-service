from __future__ import annotations
import datetime

from sqlalchemy import TIMESTAMP, String, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Role(Base):
    """
    Модель роли.

    Attributes:
        id (int): Уникальный идентификатор роли
        name (str): Наименование роли
        code (str): Уникальный код роли
        created_at (datetime): Дата создания записи
        updated_at (datetime): Дата последнего обновления

    Relationships:
        org_roles: Связь с ролями сотрудников в организациях (list[OrgRole])
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)

    # Временные метки для аудита
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=True
    )

    # Связи
    org_roles: Mapped[list["OrgRole"]] = relationship(back_populates="role")

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_roles_code",
        ),
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', code='{self.code}')>"
