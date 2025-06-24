from __future__ import annotations
import datetime

from sqlalchemy import TIMESTAMP, text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.organization import Organization


class OrgRole(Base):
    """
    Модель роли сотрудника в организации.

    Attributes:
        id (int): Уникальный идентификатор роли
        organization_id (int): ID организации
        role_id (int): ID роли
        created_at (datetime): Дата создания записи
        updated_at (datetime): Дата последнего обновления

    Relationships:
        organization: Связь с организацией (Organization)
        role: Связь с ролью (Role)
        employee_departments: Связь с сотрудниками через промежуточную таблицу (list[DepartmentEmployeeOrgRole])
    """
    __tablename__ = "org_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

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
    organization: Mapped["Organization"] = relationship(back_populates="org_roles")
    role: Mapped["Role"] = relationship(back_populates="org_roles")
    employee_departments: Mapped[list["DepartmentEmployeeOrgRole"]] = relationship(back_populates="org_role")

    __table_args__ = (
        UniqueConstraint(
            "organization_id", "role_id",
            name="uq_org_roles_organization_role",
        ),
        Index("idx_org_roles_role_id", "role_id"),
        Index("idx_org_roles_organization_id", "organization_id"),
    )

    def __repr__(self):
        return f"<OrgRole(id={self.id}, organization_id={self.organization_id}, role_id='{self.role_id}')>"
