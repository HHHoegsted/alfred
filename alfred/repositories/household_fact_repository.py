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
        details: str | None = None,
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

    def list_recent(self, limit: int = 20) -> list[HouseholdFact]:
        statement = (
            select(HouseholdFact)
            .order_by(HouseholdFact.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())