import sqlite3
from datetime import datetime
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import MaintenanceRecord


def test_maintenance_record_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    performed_at = datetime.fromisoformat("2026-04-05T10:30:00")

    try:
        with session_factory.get_session() as session:
            maintenance_record = MaintenanceRecord(
                subject="Dishwasher filter cleaning",
                category="Appliance",
                performed_at=performed_at,
                details="Removed and rinsed the filter and checked the drain well.",
                notes="Filter had a small amount of debris buildup.",
            )
            session.add(maintenance_record)
            session.commit()

        with session_factory.get_session() as session:
            stored_maintenance_record = session.query(MaintenanceRecord).one()

            maintenance_record_id = stored_maintenance_record.id
            subject = stored_maintenance_record.subject
            category = stored_maintenance_record.category
            stored_performed_at = stored_maintenance_record.performed_at
            details = stored_maintenance_record.details
            notes = stored_maintenance_record.notes
            created_at = stored_maintenance_record.created_at
            updated_at = stored_maintenance_record.updated_at
            retired_at = stored_maintenance_record.retired_at
            retired_reason = stored_maintenance_record.retired_reason

        assert maintenance_record_id is not None
        assert subject == "Dishwasher filter cleaning"
        assert category == "Appliance"
        assert stored_performed_at == performed_at
        assert details == "Removed and rinsed the filter and checked the drain well."
        assert notes == "Filter had a small amount of debris buildup."
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_maintenance_records_table_with_expected_columns(
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
                WHERE type='table' AND name='maintenance_records'
                """
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute(
                "PRAGMA table_info(maintenance_records)"
            )
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "maintenance_records"
        assert "subject" in columns
        assert "category" in columns
        assert "performed_at" in columns
        assert "details" in columns
        assert "notes" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()