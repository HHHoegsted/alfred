import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Person


def test_person_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        person = Person(
            name="Sara",
            is_household_member=True,
        )
        session.add(person)
        session.commit()

    with session_factory.get_session() as session:
        people = session.query(Person).all()

    assert len(people) == 1
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True
    assert people[0].id is not None
    assert people[0].created_at is not None


def test_init_sqlalchemy_creates_people_table_with_household_membership_column(
    tmp_path: Path,
) -> None:
    init_sqlalchemy(data_dir=tmp_path)

    db_path = get_db_path(tmp_path)
    connection = sqlite3.connect(db_path)
    try:
        table_cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='people'"
        )
        table_row = table_cursor.fetchone()

        column_cursor = connection.execute("PRAGMA table_info(people)")
        columns = [row[1] for row in column_cursor.fetchall()]
    finally:
        connection.close()

    assert table_row is not None
    assert table_row[0] == "people"
    assert "is_household_member" in columns