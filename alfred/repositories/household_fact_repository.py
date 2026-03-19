from datetime import UTC, datetime

from sqlalchemy import select

from alfred.models import HouseholdFact


class HouseholdFactRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        subject: str,
        value: str,
        details: str | None,
    ) -> HouseholdFact:
        with self.session_factory.get_session() as session:
            fact = HouseholdFact(
                subject=subject,
                value=value,
                details=details,
            )
            session.add(fact)
            session.commit()
            session.refresh(fact)
            return fact

    def get_by_id(self, fact_id: int) -> HouseholdFact | None:
        statement = select(HouseholdFact).where(HouseholdFact.id == fact_id)

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def update(
        self,
        fact: HouseholdFact,
        *,
        value: str,
        details: str | None,
    ) -> HouseholdFact:
        with self.session_factory.get_session() as session:
            persisted_fact = session.get(HouseholdFact, fact.id)

            if persisted_fact is None:
                return fact

            persisted_fact.value = value
            persisted_fact.details = details
            persisted_fact.updated_at = datetime.now(UTC)

            session.add(persisted_fact)
            session.commit()
            session.refresh(persisted_fact)
            return persisted_fact

    def retire(
        self,
        fact: HouseholdFact,
        *,
        reason: str | None,
    ) -> HouseholdFact:
        with self.session_factory.get_session() as session:
            persisted_fact = session.get(HouseholdFact, fact.id)

            if persisted_fact is None:
                return fact

            persisted_fact.retired_at = datetime.now(UTC)
            persisted_fact.retired_reason = reason

            session.add(persisted_fact)
            session.commit()
            session.refresh(persisted_fact)
            return persisted_fact

    def list_recent(self, limit: int = 10) -> list[HouseholdFact]:
        statement = (
            select(HouseholdFact)
            .where(HouseholdFact.retired_at.is_(None))
            .order_by(HouseholdFact.created_at.desc(), HouseholdFact.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))