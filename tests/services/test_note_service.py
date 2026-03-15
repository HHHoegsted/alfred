from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository
from alfred.services import NoteService


def build_service(tmp_path) -> tuple[NoteService, object]:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    session = session_factory.get_session()
    repository = NoteRepository(session)
    service = NoteService(repository)
    return service, session


def test_capture_saves_note(tmp_path) -> None:
    service, session = build_service(tmp_path)

    try:
        service.capture("Remember the milk")

        notes = service.list_recent()

        assert len(notes) == 1
        assert notes[0].text == "Remember the milk"
        assert notes[0].id is not None
        assert notes[0].created_at is not None
    finally:
        session.close()


def test_list_recent_returns_notes_in_reverse_chronological_order(tmp_path) -> None:
    service, session = build_service(tmp_path)

    try:
        service.capture("First note")
        service.capture("Second note")

        notes = service.list_recent()

        assert len(notes) == 2
        assert notes[0].text == "Second note"
        assert notes[1].text == "First note"
    finally:
        session.close()


def test_search_returns_matching_notes(tmp_path) -> None:
    service, session = build_service(tmp_path)

    try:
        service.capture("Buy Milk")
        service.capture("Walk the dog")
        service.capture("Remember milk for coffee")

        notes = service.search("milk")

        assert len(notes) == 2
        assert notes[0].text == "Remember milk for coffee"
        assert notes[1].text == "Buy Milk"
    finally:
        session.close()


def test_search_respects_limit(tmp_path) -> None:
    service, session = build_service(tmp_path)

    try:
        service.capture("milk one")
        service.capture("milk two")
        service.capture("milk three")

        notes = service.search("milk", limit=2)

        assert len(notes) == 2
        assert notes[0].text == "milk three"
        assert notes[1].text == "milk two"
    finally:
        session.close()