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

    def list_recent(self, limit: int = 20) -> list[HouseholdFact]:
        return self.repository.list_recent(limit=limit)