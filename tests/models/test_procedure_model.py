import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Procedure


def test_procedure_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            procedure_record = Procedure(
                subject="Internet is down",
                category="Troubleshooting",
                procedure="Check router power before restarting anything.",
                details="If only one device is affected, start there.",
            )
            session.add(procedure_record)
            session.commit()

        with session_factory.get_session() as session:
            stored_procedure = session.query(Procedure).one()

            procedure_id = stored_procedure.id
            subject = stored_procedure.subject
            category = stored_procedure.category
            procedure = stored_procedure.procedure
            details = stored_procedure.details
            created_at = stored_procedure.created_at
            updated_at = stored_procedure.updated_at
            retired_at = stored_procedure.retired_at
            retired_reason = stored_procedure.retired_reason

        assert procedure_id is not None
        assert subject == "Internet is down"
        assert category == "Troubleshooting"
        assert procedure == "Check router power before restarting anything."
        assert details == "If only one device is affected, start there."
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_procedures_table_with_expected_columns(
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
                WHERE type='table' AND name='procedures'
                """
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute("PRAGMA table_info(procedures)")
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "procedures"
        assert "subject" in columns
        assert "category" in columns
        assert "procedure" in columns
        assert "details" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()