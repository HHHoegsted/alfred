from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository


def test_note_repository_add_and_list_recent(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    try:
        created = repository.add("Remember the milk")

        assert created.id is not None
        assert created.created_at is not None
        assert created.text == "Remember the milk"

        notes = repository.list_recent(limit=10)

        assert len(notes) == 1
        assert notes[0].id == created.id
        assert notes[0].text == "Remember the milk"
    finally:
        session_factory.close()


def test_note_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    try:
        repository.add("First note")
        repository.add("Second note")

        notes = repository.list_recent(limit=10)

        assert len(notes) == 2
        assert notes[0].text == "Second note"
        assert notes[1].text == "First note"
    finally:
        session_factory.close()


def test_note_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)

    try:
        repository.add("First note")
        repository.add("Second note")
        repository.add("Third note")

        notes = repository.list_recent(limit=2)

        assert len(notes) == 2
        assert notes[0].text == "Third note"
        assert notes[1].text == "Second note"
    finally:
        session_factory.close()