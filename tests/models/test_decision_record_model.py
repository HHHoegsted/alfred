import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import DecisionRecord


def test_decision_record_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            record = DecisionRecord(
                summary="Use SQLAlchemy for new structured domains",
                reason=(
                    "It gives Alfred a typed persistence foundation "
                    "and eases a later move to Postgres"
                ),
            )
            session.add(record)
            session.commit()

        with session_factory.get_session() as session:
            stored_record = session.query(DecisionRecord).one()

            record_id = stored_record.id
            summary = stored_record.summary
            reason = stored_record.reason
            created_at = stored_record.created_at

        assert record_id is not None
        assert summary == "Use SQLAlchemy for new structured domains"
        assert (
            reason
            == "It gives Alfred a typed persistence foundation and eases a later move to Postgres"
        )
        assert created_at is not None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_decision_records_table_with_expected_columns(
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
    finally:
        session_factory.close()