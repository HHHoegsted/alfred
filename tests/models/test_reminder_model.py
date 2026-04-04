import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Reminder


def test_reminder_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            reminder = Reminder(
                title="Replace smoke alarm batteries",
                cadence="Twice a year",
                details="Check all alarms in the house and replace batteries as needed.",
            )
            session.add(reminder)
            session.commit()

        with session_factory.get_session() as session:
            stored_reminder = session.query(Reminder).one()

            reminder_id = stored_reminder.id
            title = stored_reminder.title
            cadence = stored_reminder.cadence
            details = stored_reminder.details
            created_at = stored_reminder.created_at
            updated_at = stored_reminder.updated_at
            retired_at = stored_reminder.retired_at
            retired_reason = stored_reminder.retired_reason

        assert reminder_id is not None
        assert title == "Replace smoke alarm batteries"
        assert cadence == "Twice a year"
        assert (
            details
            == "Check all alarms in the house and replace batteries as needed."
        )
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_reminders_table_with_expected_columns(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        db_path = get_db_path(tmp_path)
        connection = sqlite3.connect(db_path)
        try:
            table_cursor = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name='reminders'
                """
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute("PRAGMA table_info(reminders)")
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "reminders"
        assert "title" in columns
        assert "cadence" in columns
        assert "details" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()