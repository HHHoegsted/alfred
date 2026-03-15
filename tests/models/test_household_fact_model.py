import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import HouseholdFact


def test_household_fact_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        fact = HouseholdFact(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )
        session.add(fact)
        session.commit()

    with session_factory.get_session() as session:
        facts = session.query(HouseholdFact).all()

    assert len(facts) == 1
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Under kitchen sink"
    assert facts[0].details == "Turn clockwise to close"
    assert facts[0].id is not None
    assert facts[0].created_at is not None
    assert facts[0].updated_at is None
    assert facts[0].retired_at is None
    assert facts[0].retired_reason is None


def test_init_sqlalchemy_creates_household_facts_table_with_lifecycle_columns(
    tmp_path: Path,
) -> None:
    init_sqlalchemy(data_dir=tmp_path)

    db_path = get_db_path(tmp_path)
    connection = sqlite3.connect(db_path)
    try:
        table_cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='household_facts'"
        )
        table_row = table_cursor.fetchone()

        column_cursor = connection.execute("PRAGMA table_info(household_facts)")
        columns = [row[1] for row in column_cursor.fetchall()]
    finally:
        connection.close()

    assert table_row is not None
    assert table_row[0] == "household_facts"
    assert "updated_at" in columns
    assert "retired_at" in columns
    assert "retired_reason" in columns