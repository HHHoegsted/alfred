from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from alfred.models import HouseholdFact


class HouseholdFactRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        subject: str,
        value: str,
        details: str | None,
    ) -> HouseholdFact:
        fact = HouseholdFact(
            subject=subject,
            value=value,
            details=details,
        )
        self.session.add(fact)
        self.session.commit()
        self.session.refresh(fact)
        return fact

    def get_by_id(self, fact_id: int) -> HouseholdFact | None:
        statement = select(HouseholdFact).where(HouseholdFact.id == fact_id)
        return self.session.scalar(statement)

    def update(
        self,
        fact: HouseholdFact,
        *,
        value: str,
        details: str | None,
    ) -> HouseholdFact:
        fact.value = value
        fact.details = details
        fact.updated_at = datetime.now(UTC)

        self.session.add(fact)
        self.session.commit()
        self.session.refresh(fact)
        return fact

    def retire(
        self,
        fact: HouseholdFact,
        *,
        reason: str | None,
    ) -> HouseholdFact:
        fact.retired_at = datetime.now(UTC)
        fact.retired_reason = reason

        self.session.add(fact)
        self.session.commit()
        self.session.refresh(fact)
        return fact

    def list_recent(self, limit: int = 10) -> list[HouseholdFact]:
        statement = (
            select(HouseholdFact)
            .where(HouseholdFact.retired_at.is_(None))
            .order_by(HouseholdFact.created_at.desc(), HouseholdFact.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))