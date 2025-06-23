from __future__ import annotations
import datetime

from sqlalchemy import (
    TIMESTAMP,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    registration_tokens: Mapped[list["RegistrationToken"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    departments: Mapped[list["Department"]] = relationship(back_populates="organization")
    employees: Mapped[list["Employee"]] = relationship(back_populates="organization")
    org_roles: Mapped[list["OrgRole"]] = relationship(back_populates="organization")

    added_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
