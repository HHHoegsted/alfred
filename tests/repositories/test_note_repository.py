from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository


def test_note_repository_add_persists_note(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    repository.add("Remember the milk")

    notes = repository.list_recent(limit=10)

    assert len(notes) == 1
    assert notes[0].text == "Remember the milk"


def test_note_repository_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    repository.add("First note")
    repository.add("Second note")

    notes = repository.list_recent(limit=10)

    assert len(notes) == 2
    assert notes[0].text == "Second note"
    assert notes[1].text == "First note"


def test_note_repository_search_finds_matching_notes_case_insensitively(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    repository.add("Buy Milk")
    repository.add("Walk the dog")
    repository.add("Remember milk for coffee")

    notes = repository.search("milk", limit=10)

    assert len(notes) == 2
    assert notes[0].text == "Remember milk for coffee"
    assert notes[1].text == "Buy Milk"


def test_note_repository_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    repository.add("milk one")
    repository.add("milk two")
    repository.add("milk three")

    notes = repository.search("milk", limit=2)

    assert len(notes) == 2