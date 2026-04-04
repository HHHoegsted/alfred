from datetime import datetime

from alfred.models import MaintenanceRecord
from alfred.repositories import MaintenanceRecordRepository


class MaintenanceRecordService:
    def __init__(self, repository: MaintenanceRecordRepository) -> None:
        self.repository = repository

    def record(
        self,
        subject: str,
        performed_at: str,
        details: str,
        category: str | None = None,
        notes: str | None = None,
    ) -> MaintenanceRecord:
        subject = subject.strip()
        performed_at = performed_at.strip()
        details = details.strip()
        category = category.strip() if category is not None else None
        notes = notes.strip() if notes is not None else None

        if not subject:
            raise ValueError("Subject cannot be empty.")

        if not performed_at:
            raise ValueError("Performed-at timestamp cannot be empty.")

        if not details:
            raise ValueError("Details cannot be empty.")

        if category == "":
            category = None

        if notes == "":
            notes = None

        try:
            parsed_performed_at = datetime.fromisoformat(performed_at)
        except ValueError as exc:
            raise ValueError(
                "Performed-at timestamp must be a valid ISO 8601 datetime."
            ) from exc

        return self.repository.create(
            subject=subject,
            category=category,
            performed_at=parsed_performed_at,
            details=details,
            notes=notes,
        )

    def update(
        self,
        maintenance_record_id: int,
        performed_at: str,
        details: str,
        category: str | None = None,
        notes: str | None = None,
    ) -> MaintenanceRecord:
        maintenance_record = self.repository.get_by_id(maintenance_record_id)
        if maintenance_record is None:
            raise ValueError(
                f"Maintenance record {maintenance_record_id} was not found."
            )

        if maintenance_record.retired_at is not None:
            raise ValueError(
                f"Maintenance record {maintenance_record_id} is retired and cannot be updated."
            )

        performed_at = performed_at.strip()
        details = details.strip()
        category = category.strip() if category is not None else None
        notes = notes.strip() if notes is not None else None

        if not performed_at:
            raise ValueError("Performed-at timestamp cannot be empty.")

        if not details:
            raise ValueError("Details cannot be empty.")

        if category == "":
            category = None

        if notes == "":
            notes = None

        try:
            parsed_performed_at = datetime.fromisoformat(performed_at)
        except ValueError as exc:
            raise ValueError(
                "Performed-at timestamp must be a valid ISO 8601 datetime."
            ) from exc

        return self.repository.update(
            maintenance_record,
            category=category,
            performed_at=parsed_performed_at,
            details=details,
            notes=notes,
        )

    def retire(
        self,
        maintenance_record_id: int,
        reason: str | None = None,
    ) -> MaintenanceRecord:
        maintenance_record = self.repository.get_by_id(maintenance_record_id)
        if maintenance_record is None:
            raise ValueError(
                f"Maintenance record {maintenance_record_id} was not found."
            )

        if maintenance_record.retired_at is not None:
            raise ValueError(
                f"Maintenance record {maintenance_record_id} is already retired."
            )

        reason = reason.strip() if reason is not None else None
        if reason == "":
            reason = None

        return self.repository.retire(
            maintenance_record,
            reason=reason,
        )

    def list_recent(self, limit: int = 10) -> list[MaintenanceRecord]:
        return self.repository.list_recent(limit=limit)