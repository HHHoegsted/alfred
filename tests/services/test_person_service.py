from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository
from alfred.services import NoteService


def test_note_service_capture_saves_note(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    try:
        note = service.capture("Remember the milk")

        assert note.id is not None
        assert note.created_at is not None
        assert note.text == "Remember the milk"

        notes = service.list_recent(limit=10)

        assert len(notes) == 1
        assert notes[0].text == "Remember the milk"
    finally:
        session_factory.close()


def test_note_service_capture_strips_note_text(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    try:
        note = service.capture("   Remember the milk   ")

        assert note.text == "Remember the milk"
    finally:
        session_factory.close()


def test_note_service_capture_rejects_empty_note(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    try:
        with pytest.raises(ValueError, match="Note cannot be empty."):
            service.capture("   ")
    finally:
        session_factory.close()


def test_note_service_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    try:
        service.capture("First note")
        service.capture("Second note")

        notes = service.list_recent(limit=10)

        assert len(notes) == 2
        assert notes[0].text == "Second note"
        assert notes[1].text == "First note"
    finally:
        session_factory.close()


def test_note_service_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = NoteRepository(session_factory)
    service = NoteService(repository)

    try:
        service.capture("First note")
        service.capture("Second note")
        service.capture("Third note")

        notes = service.list_recent(limit=2)

        assert len(notes) == 2
        assert notes[0].text == "Third note"
        assert notes[1].text == "Second note"
    finally:
        session_factory.close()