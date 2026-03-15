from alfred.models import HouseholdFact
from alfred.repositories import HouseholdFactRepository


class HouseholdFactService:
    def __init__(self, repository: HouseholdFactRepository) -> None:
        self.repository = repository

    def record(
        self,
        subject: str,
        value: str,
        details: str | None = None,
    ) -> HouseholdFact:
        subject = subject.strip()
        value = value.strip()
        details = details.strip() if details is not None else None

        if not subject:
            raise ValueError("Subject cannot be empty.")

        if not value:
            raise ValueError("Value cannot be empty.")

        if details == "":
            details = None

        return self.repository.create(
            subject=subject,
            value=value,
            details=details,
        )

    def update(
        self,
        fact_id: int,
        value: str,
        details: str | None = None,
    ) -> HouseholdFact:
        fact = self.repository.get_by_id(fact_id)
        if fact is None:
            raise ValueError(f"Household fact {fact_id} was not found.")

        if fact.retired_at is not None:
            raise ValueError(f"Household fact {fact_id} is retired and cannot be updated.")

        value = value.strip()
        details = details.strip() if details is not None else None

        if not value:
            raise ValueError("Value cannot be empty.")

        if details == "":
            details = None

        return self.repository.update(
            fact,
            value=value,
            details=details,
        )

    def retire(
        self,
        fact_id: int,
        reason: str | None = None,
    ) -> HouseholdFact:
        fact = self.repository.get_by_id(fact_id)
        if fact is None:
            raise ValueError(f"Household fact {fact_id} was not found.")

        if fact.retired_at is not None:
            raise ValueError(f"Household fact {fact_id} is already retired.")

        reason = reason.strip() if reason is not None else None
        if reason == "":
            reason = None

        return self.repository.retire(
            fact,
            reason=reason,
        )

    def list_recent(self, limit: int = 20) -> list[HouseholdFact]:
        return self.repository.list_recent(limit=limit)