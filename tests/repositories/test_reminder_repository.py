from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import Reminder
from alfred.repositories import ReminderRepository


def test_reminder_repository_create_and_list_recent(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.title == "Replace smoke alarm batteries"
        assert created.cadence == "Twice a year"
        assert (
            created.details
            == "Check all alarms in the house and replace batteries as needed."
        )

        reminders = repository.list_recent(limit=10)

        assert len(reminders) == 1
        assert reminders[0].id == created.id
        assert reminders[0].title == "Replace smoke alarm batteries"
        assert reminders[0].cadence == "Twice a year"
        assert (
            reminders[0].details
            == "Check all alarms in the house and replace batteries as needed."
        )
    finally:
        session_factory.close()


def test_reminder_repository_get_by_id_returns_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        reminder = repository.get_by_id(created.id)

        assert reminder is not None
        assert reminder.id == created.id
        assert reminder.title == "Replace smoke alarm batteries"
        assert reminder.cadence == "Twice a year"
        assert (
            reminder.details
            == "Check all alarms in the house and replace batteries as needed."
        )
    finally:
        session_factory.close()


def test_reminder_repository_get_by_id_returns_none_for_missing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        reminder = repository.get_by_id(9999)

        assert reminder is None
    finally:
        session_factory.close()


def test_reminder_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        repository.create(
            title="First reminder",
            cadence=None,
            details=None,
        )
        repository.create(
            title="Second reminder",
            cadence=None,
            details=None,
        )

        reminders = repository.list_recent(limit=10)

        assert len(reminders) == 2
        assert reminders[0].title == "Second reminder"
        assert reminders[1].title == "First reminder"
    finally:
        session_factory.close()


def test_reminder_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        repository.create(
            title="First reminder",
            cadence=None,
            details=None,
        )
        repository.create(
            title="Second reminder",
            cadence=None,
            details=None,
        )
        repository.create(
            title="Third reminder",
            cadence=None,
            details=None,
        )

        reminders = repository.list_recent(limit=2)

        assert len(reminders) == 2
        assert reminders[0].title == "Third reminder"
        assert reminders[1].title == "Second reminder"
    finally:
        session_factory.close()


def test_reminder_repository_update_updates_existing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        updated = repository.update(
            reminder=created,
            cadence="Every 6 months",
            details="Check all alarms and test them after replacing batteries.",
        )

        assert updated is not None
        assert updated.id == created.id
        assert updated.title == "Replace smoke alarm batteries"
        assert updated.cadence == "Every 6 months"
        assert (
            updated.details
            == "Check all alarms and test them after replacing batteries."
        )
        assert updated.updated_at is not None
    finally:
        session_factory.close()


def test_reminder_repository_update_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(Reminder, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        updated = repository.update(
            reminder=created,
            cadence="Every 6 months",
            details="Check all alarms and test them after replacing batteries.",
        )

        assert updated is created
        assert updated.id == created.id
        assert updated.cadence == "Twice a year"
        assert (
            updated.details
            == "Check all alarms in the house and replace batteries as needed."
        )
        assert updated.updated_at is None
    finally:
        session_factory.close()


def test_reminder_repository_retire_marks_record_as_retired(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        retired = repository.retire(
            reminder=created,
            reason="No longer needed after installing wired alarms",
        )

        assert retired is not None
        assert retired.id == created.id
        assert retired.retired_at is not None
        assert retired.retired_reason == "No longer needed after installing wired alarms"

        reminders = repository.list_recent(limit=10)
        assert len(reminders) == 0
    finally:
        session_factory.close()


def test_reminder_repository_retire_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)

    try:
        created = repository.create(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(Reminder, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        retired = repository.retire(
            reminder=created,
            reason="No longer needed after installing wired alarms",
        )

        assert retired is created
        assert retired.id == created.id
        assert retired.retired_at is None
        assert retired.retired_reason is None
    finally:
        session_factory.close()