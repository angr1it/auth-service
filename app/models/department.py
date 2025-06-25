from __future__ import annotations
import datetime

from sqlalchemy import TIMESTAMP, String, ForeignKey, text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.organization import Organization


class Department(Base):
    """
    Модель отдела организации.

    Attributes:
        id (int): Уникальный идентификатор отдела
        name (str): Название отдела
        path (str | None): Материализованный путь (от топа до отдела)
        organization_id (int): ID организации
        parent_id (int | None): ID родительского отдела
        created_at (datetime): Дата создания записи
        updated_at (datetime): Дата последнего обновления

    Relationships:
        organization: Связь с организацией (Organization)
        parent: Связь с родительским отделом (Department)
        children: Связь с дочерними отделами (list[Department])
        employee_roles: Связь с сотрудниками через промежуточную таблицу (list[DepartmentEmployeeOrgRole])
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str | None] = mapped_column(String, nullable=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)

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
    organization: Mapped["Organization"] = relationship(back_populates="departments")
    parent: Mapped["Department"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Department"]] = relationship(back_populates="parent")
    employee_roles: Mapped[list["DepartmentEmployeeOrgRole"]] = relationship(back_populates="department")

    __table_args__ = (
        UniqueConstraint("name", "organization_id", name="uq_departments_name_organization"),
        Index("idx_departments_path", "path"),
        Index("idx_departments_organization_id", "organization_id"),
        Index("idx_departments_parent_id", "parent_id"),
    )

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', path='{self.path}')>"
