from datetime import UTC, datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from alfred.db import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    retired_at: Mapped[datetime | None] = mapped_column(nullable=True)

    subject: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    performed_at: Mapped[datetime] = mapped_column()
    details: Mapped[str] = mapped_column(Text)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    retired_reason: Mapped[str | None] = mapped_column(Text, nullable=True)