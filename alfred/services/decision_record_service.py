from alfred.models import DecisionRecord
from alfred.repositories import DecisionRecordRepository


class DecisionRecordService:
    def __init__(self, repository: DecisionRecordRepository) -> None:
        self.repository = repository

    def record(self, summary: str, reason: str) -> DecisionRecord:
        cleaned_summary = summary.strip()
        cleaned_reason = reason.strip()

        if not cleaned_summary:
            raise ValueError("Decision summary cannot be empty.")

        if not cleaned_reason:
            raise ValueError("Decision reason cannot be empty.")

        return self.repository.create(
            summary=cleaned_summary,
            reason=cleaned_reason,
        )

    def list_recent(self, limit: int = 20) -> list[DecisionRecord]:
        return self.repository.list_recent(limit=limit)