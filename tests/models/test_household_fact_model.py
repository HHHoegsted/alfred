import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import HouseholdFact


def test_household_fact_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            fact = HouseholdFact(
                subject="Water shutoff valve",
                value="Under kitchen sink",
                details="Turn clockwise to close.",
            )
            session.add(fact)
            session.commit()

        with session_factory.get_session() as session:
            stored_fact = session.query(HouseholdFact).one()

            fact_id = stored_fact.id
            subject = stored_fact.subject
            value = stored_fact.value
            details = stored_fact.details
            created_at = stored_fact.created_at
            updated_at = stored_fact.updated_at
            retired_at = stored_fact.retired_at
            retired_reason = stored_fact.retired_reason

        assert fact_id is not None
        assert subject == "Water shutoff valve"
        assert value == "Under kitchen sink"
        assert details == "Turn clockwise to close."
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_household_facts_table_with_expected_columns(
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
                WHERE type='table' AND name='household_facts'
                """
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute("PRAGMA table_info(household_facts)")
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "household_facts"
        assert "subject" in columns
        assert "value" in columns
        assert "details" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()