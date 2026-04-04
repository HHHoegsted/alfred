from alfred.models import Reminder
from alfred.repositories import ReminderRepository


class ReminderService:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def record(
        self,
        title: str,
        cadence: str | None = None,
        details: str | None = None,
    ) -> Reminder:
        title = title.strip()
        cadence = cadence.strip() if cadence is not None else None
        details = details.strip() if details is not None else None

        if not title:
            raise ValueError("Title cannot be empty.")

        if cadence == "":
            cadence = None

        if details == "":
            details = None

        return self.repository.create(
            title=title,
            cadence=cadence,
            details=details,
        )

    def update(
        self,
        reminder_id: int,
        cadence: str | None = None,
        details: str | None = None,
    ) -> Reminder:
        reminder = self.repository.get_by_id(reminder_id)
        if reminder is None:
            raise ValueError(f"Reminder {reminder_id} was not found.")

        if reminder.retired_at is not None:
            raise ValueError(
                f"Reminder {reminder_id} is retired and cannot be updated."
            )

        cadence = cadence.strip() if cadence is not None else None
        details = details.strip() if details is not None else None

        if cadence == "":
            cadence = None

        if details == "":
            details = None

        return self.repository.update(
            reminder,
            cadence=cadence,
            details=details,
        )

    def retire(
        self,
        reminder_id: int,
        reason: str | None = None,
    ) -> Reminder:
        reminder = self.repository.get_by_id(reminder_id)
        if reminder is None:
            raise ValueError(f"Reminder {reminder_id} was not found.")

        if reminder.retired_at is not None:
            raise ValueError(f"Reminder {reminder_id} is already retired.")

        reason = reason.strip() if reason is not None else None
        if reason == "":
            reason = None

        return self.repository.retire(
            reminder,
            reason=reason,
        )

    def list_recent(self, limit: int = 10) -> list[Reminder]:
        return self.repository.list_recent(limit=limit)