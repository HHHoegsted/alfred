from datetime import UTC, datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from alfred.db import Base


class HouseholdFact(Base):
    __tablename__ = "household_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    subject: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(Text)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)