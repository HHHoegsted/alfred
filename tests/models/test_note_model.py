import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Note


def test_note_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        note = Note(text="Remember the milk")
        session.add(note)
        session.commit()

    with session_factory.get_session() as session:
        notes = session.query(Note).all()

    assert len(notes) == 1
    assert notes[0].text == "Remember the milk"
    assert notes[0].id is not None
    assert notes[0].created_at is not None


def test_init_sqlalchemy_creates_notes_table_with_text_column(tmp_path: Path) -> None:
    init_sqlalchemy(data_dir=tmp_path)

    db_path = get_db_path(tmp_path)
    connection = sqlite3.connect(db_path)
    try:
        table_cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='notes'"
        )
        table_row = table_cursor.fetchone()

        column_cursor = connection.execute("PRAGMA table_info(notes)")
        columns = [row[1] for row in column_cursor.fetchall()]
    finally:
        connection.close()

    assert table_row is not None
    assert table_row[0] == "notes"
    assert "text" in columns