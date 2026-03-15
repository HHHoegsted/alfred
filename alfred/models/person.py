from datetime import datetime, UTC

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from alfred.db import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    name: Mapped[str] = mapped_column(String(255))
    is_household_member: Mapped[bool] = mapped_column(default=False)