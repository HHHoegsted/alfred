from datetime import UTC, datetime

from sqlalchemy import select

from alfred.models import Reminder


class ReminderRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        title: str,
        cadence: str | None,
        details: str | None,
    ) -> Reminder:
        with self.session_factory.get_session() as session:
            reminder = Reminder(
                title=title,
                cadence=cadence,
                details=details,
            )
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            return reminder

    def get_by_id(self, reminder_id: int) -> Reminder | None:
        statement = select(Reminder).where(Reminder.id == reminder_id)

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def update(
        self,
        reminder: Reminder,
        *,
        cadence: str | None,
        details: str | None,
    ) -> Reminder:
        with self.session_factory.get_session() as session:
            persisted_reminder = session.get(
                Reminder,
                reminder.id,
            )

            if persisted_reminder is None:
                return reminder

            persisted_reminder.cadence = cadence
            persisted_reminder.details = details
            persisted_reminder.updated_at = datetime.now(UTC)

            session.add(persisted_reminder)
            session.commit()
            session.refresh(persisted_reminder)
            return persisted_reminder

    def retire(
        self,
        reminder: Reminder,
        *,
        reason: str | None,
    ) -> Reminder:
        with self.session_factory.get_session() as session:
            persisted_reminder = session.get(
                Reminder,
                reminder.id,
            )

            if persisted_reminder is None:
                return reminder

            persisted_reminder.retired_at = datetime.now(UTC)
            persisted_reminder.retired_reason = reason

            session.add(persisted_reminder)
            session.commit()
            session.refresh(persisted_reminder)
            return persisted_reminder

    def list_recent(self, limit: int = 10) -> list[Reminder]:
        statement = (
            select(Reminder)
            .where(Reminder.retired_at.is_(None))
            .order_by(Reminder.created_at.desc(), Reminder.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))