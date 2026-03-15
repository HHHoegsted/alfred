import sqlite3

from alfred.bootstrap import get_db_path, init_sqlalchemy


def test_init_sqlalchemy_creates_people_table_with_household_membership_column(
    tmp_path,
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