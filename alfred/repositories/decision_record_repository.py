from sqlalchemy import select

from alfred.models import DecisionRecord


class DecisionRecordRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(self, summary: str, reason: str) -> DecisionRecord:
        with self.session_factory.get_session() as session:
            record = DecisionRecord(summary=summary, reason=reason)
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def list_recent(self, limit: int = 20) -> list[DecisionRecord]:
        statement = (
            select(DecisionRecord)
            .order_by(DecisionRecord.created_at.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement).all())