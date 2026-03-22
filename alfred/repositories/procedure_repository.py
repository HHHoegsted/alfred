from datetime import UTC, datetime

from sqlalchemy import select

from alfred.models import Procedure


class ProcedureRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        subject: str,
        category: str | None,
        procedure: str,
        details: str | None,
    ) -> Procedure:
        with self.session_factory.get_session() as session:
            record = Procedure(
                subject=subject,
                category=category,
                procedure=procedure,
                details=details,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_by_id(self, procedure_id: int) -> Procedure | None:
        statement = select(Procedure).where(Procedure.id == procedure_id)

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def update(
        self,
        procedure_record: Procedure,
        *,
        category: str | None,
        procedure: str,
        details: str | None,
    ) -> Procedure:
        with self.session_factory.get_session() as session:
            persisted_record = session.get(
                Procedure,
                procedure_record.id,
            )

            if persisted_record is None:
                return procedure_record

            persisted_record.category = category
            persisted_record.procedure = procedure
            persisted_record.details = details
            persisted_record.updated_at = datetime.now(UTC)

            session.add(persisted_record)
            session.commit()
            session.refresh(persisted_record)
            return persisted_record

    def retire(
        self,
        procedure_record: Procedure,
        *,
        reason: str | None,
    ) -> Procedure:
        with self.session_factory.get_session() as session:
            persisted_record = session.get(
                Procedure,
                procedure_record.id,
            )

            if persisted_record is None:
                return procedure_record

            persisted_record.retired_at = datetime.now(UTC)
            persisted_record.retired_reason = reason

            session.add(persisted_record)
            session.commit()
            session.refresh(persisted_record)
            return persisted_record

    def list_recent(self, limit: int = 10) -> list[Procedure]:
        statement = (
            select(Procedure)
            .where(Procedure.retired_at.is_(None))
            .order_by(Procedure.created_at.desc(), Procedure.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))