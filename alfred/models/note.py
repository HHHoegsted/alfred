from datetime import datetime, UTC

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from alfred.db import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    text: Mapped[str] = mapped_column(Text)