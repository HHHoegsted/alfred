import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Procedure


def test_procedure_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

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
        procedures = session.query(Procedure).all()

    assert len(procedures) == 1
    assert procedures[0].subject == "Internet is down"
    assert procedures[0].category == "Troubleshooting"
    assert (
        procedures[0].procedure
        == "Check router power before restarting anything."
    )
    assert procedures[0].details == "If only one device is affected, start there."
    assert procedures[0].id is not None
    assert procedures[0].created_at is not None
    assert procedures[0].updated_at is None
    assert procedures[0].retired_at is None
    assert procedures[0].retired_reason is None


def test_init_sqlalchemy_creates_procedures_table_with_expected_columns(
    tmp_path: Path,
) -> None:
    init_sqlalchemy(data_dir=tmp_path)

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