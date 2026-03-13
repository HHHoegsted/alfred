import sqlite3
from pathlib import Path

from alfred.db import SQLiteConnectionFactory
from alfred.repositories import NoteRepository


def build_repository(tmp_path: Path) -> NoteRepository:
    db_path = tmp_path / "test_alfred.db"
    connection_factory = SQLiteConnectionFactory(db_path)
    connection_factory.init_db()
    return NoteRepository(connection_factory)


def test_add_inserts_note(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)

    repository.add("Remember the milk")

    notes = repository.list_recent()

    assert len(notes) == 1
    assert isinstance(notes[0], sqlite3.Row)
    assert notes[0]["text"] == "Remember the milk"


def test_list_recent_returns_newest_first(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)

    repository.add("First note")
    repository.add("Second note")

    notes = repository.list_recent()

    assert len(notes) == 2
    assert notes[0]["text"] == "Second note"
    assert notes[1]["text"] == "First note"


def test_search_finds_matching_notes_case_insensitively(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)

    repository.add("Buy Milk")
    repository.add("Walk the dog")
    repository.add("Remember milk for coffee")

    notes = repository.search("milk")

    assert len(notes) == 2
    assert notes[0]["text"] == "Remember milk for coffee"
    assert notes[1]["text"] == "Buy Milk"


def test_search_respects_limit(tmp_path: Path) -> None:
    repository = build_repository(tmp_path)

    repository.add("milk one")
    repository.add("milk two")
    repository.add("milk three")

    notes = repository.search("milk", limit=2)

    assert len(notes) == 2
    assert notes[0]["text"] == "milk three"
    assert notes[1]["text"] == "milk two"
