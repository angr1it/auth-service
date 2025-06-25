from __future__ import annotations
import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.employee import Employee
from models.department import Department
from models.org_role import OrgRole


class DepartmentEmployeeOrgRole(Base):
    """
    Модель связи сотрудника с отделом и ролью.

    Attributes:
        id (int): Уникальный идентификатор связи сотрудника с отделом и ролью
        employee_id (int): ID сотрудника
        department_id (int): ID отдела
        org_role_id (int): ID роли
        created_at (datetime): Дата создания записи
        updated_at (datetime): Дата последнего обновления

    Relationships:
        employee: Связь с сотрудником (Employee)
        department: Связь с отделом (Department)
        org_role: Связь с ролью (OrgRole)
    """
    __tablename__ = "department_employee_org_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    org_role_id: Mapped[int] = mapped_column(ForeignKey("org_roles.id"), nullable=False)

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
    employee: Mapped["Employee"] = relationship(back_populates="department_roles")
    department: Mapped["Department"] = relationship(back_populates="employee_roles")
    org_role: Mapped["OrgRole"] = relationship(back_populates="employee_departments")

    __table_args__ = (
        UniqueConstraint(
            "department_id", "employee_id", "org_role_id",
            name="uq_department_employee_org_roles"
        ),
        Index("idx_department_employee_org_roles_employee_id", "employee_id"),
        Index("idx_department_employee_org_roles_department_id", "department_id"),
        Index("idx_department_employee_org_roles_org_role_id", "org_role_id"),
    )

    def __repr__(self):
        return (
            f"<DepartmentEmployeeOrgRole(id={self.id}, "
            f"employee_id={self.employee_id}, "
            f"department_id={self.department_id}, "
            f"org_role_id={self.org_role_id})>"
        )
