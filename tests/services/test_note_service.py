from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository
from alfred.services import NoteService


def test_note_service_capture_saves_note(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    note = service.capture("Remember the milk")

    assert note.id is not None
    assert note.text == "Remember the milk"

    notes = service.list_recent(limit=10)
    assert len(notes) == 1
    assert notes[0].text == "Remember the milk"


def test_note_service_capture_rejects_empty_text(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    with pytest.raises(ValueError, match="Note cannot be empty."):
        service.capture("   ")


def test_note_service_capture_strips_text(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    note = service.capture("  Remember the milk  ")

    assert note.text == "Remember the milk"


def test_note_service_list_recent_returns_notes_in_reverse_chronological_order(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    service.capture("First note")
    service.capture("Second note")

    notes = service.list_recent(limit=10)

    assert len(notes) == 2
    assert notes[0].text == "Second note"
    assert notes[1].text == "First note"


def test_note_service_search_returns_matching_notes(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    service.capture("Buy Milk")
    service.capture("Walk the dog")
    service.capture("Remember milk for coffee")

    notes = service.search("milk", limit=10)

    assert len(notes) == 2
    assert notes[0].text == "Remember milk for coffee"
    assert notes[1].text == "Buy Milk"


def test_note_service_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    service.capture("milk one")
    service.capture("milk two")
    service.capture("milk three")

    notes = service.search("milk", limit=2)

    assert len(notes) == 2