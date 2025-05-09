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


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    jti: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))
    revoked_at: Mapped[dt.datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    added_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
