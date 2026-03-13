import sqlite3
from pathlib import Path

from alfred.db import SQLiteConnectionFactory
from alfred.repositories import NoteRepository
from alfred.services import NoteService


def build_service(tmp_path: Path) -> NoteService:
    db_path = tmp_path / "test_alfred.db"
    connection_factory = SQLiteConnectionFactory(db_path)
    connection_factory.init_db()
    repository = NoteRepository(connection_factory)
    return NoteService(repository)


def test_capture_saves_note(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    service.capture("Remember the milk")

    notes = service.list_recent()

    assert len(notes) == 1
    assert isinstance(notes[0], sqlite3.Row)
    assert notes[0]["text"] == "Remember the milk"


def test_list_recent_returns_notes_in_reverse_chronological_order(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    service.capture("First note")
    service.capture("Second note")

    notes = service.list_recent()

    assert len(notes) == 2
    assert notes[0]["text"] == "Second note"
    assert notes[1]["text"] == "First note"


def test_search_returns_matching_notes(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    service.capture("Buy Milk")
    service.capture("Walk the dog")
    service.capture("Remember milk for coffee")

    notes = service.search("milk")

    assert len(notes) == 2
    assert notes[0]["text"] == "Remember milk for coffee"
    assert notes[1]["text"] == "Buy Milk"


def test_search_respects_limit(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    service.capture("milk one")
    service.capture("milk two")
    service.capture("milk three")

    notes = service.search("milk", limit=2)

    assert len(notes) == 2
    assert notes[0]["text"] == "milk three"
    assert notes[1]["text"] == "milk two"
