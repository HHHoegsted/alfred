from datetime import datetime, UTC

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from alfred.db import Base


class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    summary: Mapped[str] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text)