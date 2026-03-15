from sqlalchemy import select
from sqlalchemy.orm import Session

from alfred.models import DecisionRecord


class DecisionRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, summary: str, reason: str) -> DecisionRecord:
        record = DecisionRecord(summary=summary, reason=reason)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def list_recent(self, limit: int = 20) -> list[DecisionRecord]:
        statement = (
            select(DecisionRecord)
            .order_by(DecisionRecord.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())