from __future__ import annotations
import datetime as dt

from sqlalchemy import (
    String,
    TIMESTAMP,
    ForeignKey,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class RegistrationToken(Base):
    __tablename__ = "registration_tokens"
    jti: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))
    used_at: Mapped[dt.datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    operator_id: Mapped[int] = mapped_column(nullable=True)

    organization: Mapped["Organization"] = relationship(
        back_populates="registration_tokens"
    )
    creator: Mapped["User"] = relationship(back_populates="created_registration_tokens")

    added_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
