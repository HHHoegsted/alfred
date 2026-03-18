import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import DecisionRecord


def test_decision_record_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        record = DecisionRecord(
            summary="Use SQLAlchemy for new structured domains",
            reason="It gives Alfred a typed persistence foundation and eases a later move to Postgres",
        )
        session.add(record)
        session.commit()

    with session_factory.get_session() as session:
        records = session.query(DecisionRecord).all()

    assert len(records) == 1
    assert records[0].summary == "Use SQLAlchemy for new structured domains"
    assert (
        records[0].reason
        == "It gives Alfred a typed persistence foundation and eases a later move to Postgres"
    )
    assert records[0].id is not None
    assert records[0].created_at is not None

def test_init_sqlalchemy_creates_decision_records_table_with_expected_columns(
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
            WHERE type='table' AND name='decision_records'
            """
        )
        table_row = table_cursor.fetchone()

        column_cursor = connection.execute("PRAGMA table_info(decision_records)")
        columns = [row[1] for row in column_cursor.fetchall()]
    finally:
        connection.close()

    assert table_row is not None
    assert table_row[0] == "decision_records"
    assert "summary" in columns
    assert "reason" in columns
