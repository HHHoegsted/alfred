from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import ReminderRepository
from alfred.services import ReminderService


def test_reminder_service_record_saves_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        assert reminder.id is not None
        assert reminder.title == "Replace smoke alarm batteries"
        assert reminder.cadence == "Twice a year"
        assert (
            reminder.details
            == "Check all alarms in the house and replace batteries as needed."
        )

        reminders = service.list_recent(limit=10)
        assert len(reminders) == 1
        assert reminders[0].title == "Replace smoke alarm batteries"
        assert reminders[0].cadence == "Twice a year"
        assert (
            reminders[0].details
            == "Check all alarms in the house and replace batteries as needed."
        )
    finally:
        session_factory.close()


def test_reminder_service_record_rejects_empty_title(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        with pytest.raises(ValueError, match="Title cannot be empty."):
            service.record(
                title="   ",
                cadence="Twice a year",
                details="Check all alarms in the house and replace batteries as needed.",
            )
    finally:
        session_factory.close()


def test_reminder_service_record_strips_inputs(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="  Replace smoke alarm batteries  ",
            cadence="  Twice a year  ",
            details="  Check all alarms in the house and replace batteries as needed.  ",
        )

        assert reminder.title == "Replace smoke alarm batteries"
        assert reminder.cadence == "Twice a year"
        assert (
            reminder.details
            == "Check all alarms in the house and replace batteries as needed."
        )
    finally:
        session_factory.close()


def test_reminder_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="   ",
            details="   ",
        )

        assert reminder.cadence is None
        assert reminder.details is None
    finally:
        session_factory.close()


def test_reminder_service_update_updates_existing_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        updated_reminder = service.update(
            reminder_id=reminder.id,
            cadence="Every 6 months",
            details="Check all alarms and test them after replacing batteries.",
        )

        assert updated_reminder.id == reminder.id
        assert updated_reminder.title == "Replace smoke alarm batteries"
        assert updated_reminder.cadence == "Every 6 months"
        assert (
            updated_reminder.details
            == "Check all alarms and test them after replacing batteries."
        )
        assert updated_reminder.updated_at is not None
    finally:
        session_factory.close()


def test_reminder_service_update_rejects_missing_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Reminder 9999 was not found.",
        ):
            service.update(
                reminder_id=9999,
                cadence="Every 6 months",
                details="Check all alarms and test them after replacing batteries.",
            )
    finally:
        session_factory.close()


def test_reminder_service_update_rejects_retired_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        service.retire(
            reminder_id=reminder.id,
            reason="No longer needed after installing wired alarms",
        )

        with pytest.raises(
            ValueError,
            match=(
                f"Reminder {reminder.id} is retired "
                "and cannot be updated."
            ),
        ):
            service.update(
                reminder_id=reminder.id,
                cadence="Every 6 months",
                details="Check all alarms and test them after replacing batteries.",
            )
    finally:
        session_factory.close()


def test_reminder_service_update_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        updated_reminder = service.update(
            reminder_id=reminder.id,
            cadence="   ",
            details="   ",
        )

        assert updated_reminder.cadence is None
        assert updated_reminder.details is None
    finally:
        session_factory.close()


def test_reminder_service_retire_retires_existing_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        retired_reminder = service.retire(
            reminder_id=reminder.id,
            reason="No longer needed after installing wired alarms",
        )

        assert retired_reminder.id == reminder.id
        assert retired_reminder.retired_at is not None
        assert retired_reminder.retired_reason == "No longer needed after installing wired alarms"

        reminders = service.list_recent(limit=10)
        assert len(reminders) == 0
    finally:
        session_factory.close()


def test_reminder_service_retire_rejects_missing_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Reminder 9999 was not found.",
        ):
            service.retire(
                reminder_id=9999,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_reminder_service_retire_rejects_already_retired_reminder(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        service.retire(
            reminder_id=reminder.id,
            reason="No longer needed after installing wired alarms",
        )

        with pytest.raises(
            ValueError,
            match=f"Reminder {reminder.id} is already retired.",
        ):
            service.retire(
                reminder_id=reminder.id,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_reminder_service_retire_normalizes_blank_reason_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        retired_reminder = service.retire(
            reminder_id=reminder.id,
            reason="   ",
        )

        assert retired_reminder.retired_at is not None
        assert retired_reminder.retired_reason is None
    finally:
        session_factory.close()


def test_reminder_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        service.record(
            title="First reminder",
            cadence=None,
            details=None,
        )
        service.record(
            title="Second reminder",
            cadence=None,
            details=None,
        )

        reminders = service.list_recent(limit=10)

        assert len(reminders) == 2
        assert reminders[0].title == "Second reminder"
        assert reminders[1].title == "First reminder"
    finally:
        session_factory.close()


def test_reminder_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        service.record(
            title="First reminder",
            cadence=None,
            details=None,
        )
        service.record(
            title="Second reminder",
            cadence=None,
            details=None,
        )
        service.record(
            title="Third reminder",
            cadence=None,
            details=None,
        )

        reminders = service.list_recent(limit=2)

        assert len(reminders) == 2
        assert reminders[0].title == "Third reminder"
        assert reminders[1].title == "Second reminder"
    finally:
        session_factory.close()


def test_reminder_service_list_recent_uses_default_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ReminderRepository(session_factory)
    service = ReminderService(repository)

    try:
        for index in range(12):
            service.record(
                title=f"Reminder {index}",
                cadence=None,
                details=None,
            )

        reminders = service.list_recent()

        assert len(reminders) == 10
        assert reminders[0].title == "Reminder 11"
        assert reminders[-1].title == "Reminder 2"
    finally:
        session_factory.close()