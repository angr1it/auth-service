from __future__ import annotations
import datetime

from sqlalchemy import TIMESTAMP, String, ForeignKey, text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.organization import Organization
from models.user import User


class Employee(Base):
    """
    Модель сотрудника организации.

    Attributes:
        id (int): Уникальный идентификатор сотрудника
        first_name (str): Имя сотрудника
        last_name (str): Фамилия сотрудника
        operator_id (int | None): ID оператора из внешней CRM системы
        organization_id (int): ID организации
        user_id (int | None): ID связанного пользователя
        created_at (datetime): Дата создания записи
        updated_at (datetime): Дата последнего обновления

    Relationships:
        organization: Связь с организацией (Organization)
        user: Связь с пользователем (User)
        department_roles: Связь с отделами через промежуточную таблицу (list[DepartmentEmployeeOrgRole])
    """
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    operator_id: Mapped[int | None] = mapped_column(nullable=True)  # ID из внешней CRM системы
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

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
    organization: Mapped["Organization"] = relationship(back_populates="employees")
    user: Mapped["User"] = relationship(back_populates="employee")
    department_roles: Mapped[list["DepartmentEmployeeOrgRole"]] = relationship(back_populates="employee")

    __table_args__ = (
        Index("idx_employees_organization_id", "organization_id"),
        Index("idx_employees_user_id", "user_id"),
        Index(
            "uq_employees_organization_operator",
            "organization_id", "operator_id",
            unique=True,
            postgresql_where=text("operator_id IS NOT NULL"),
        ),
    )

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}')>"

    @property
    def full_name(self):
        """Полное имя сотрудника (имя + фамилия)."""
        return f"{self.first_name} {self.last_name}"
