from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import NoteRepository


def build_repository(tmp_path) -> tuple[NoteRepository, object]:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    session = session_factory.get_session()
    repository = NoteRepository(session)
    return repository, session


def test_add_inserts_note(tmp_path) -> None:
    repository, session = build_repository(tmp_path)

    try:
        repository.add("Remember the milk")

        notes = repository.list_recent()

        assert len(notes) == 1
        assert notes[0].text == "Remember the milk"
        assert notes[0].id is not None
        assert notes[0].created_at is not None
    finally:
        session.close()


def test_list_recent_returns_newest_first(tmp_path) -> None:
    repository, session = build_repository(tmp_path)

    try:
        repository.add("First note")
        repository.add("Second note")

        notes = repository.list_recent()

        assert len(notes) == 2
        assert notes[0].text == "Second note"
        assert notes[1].text == "First note"
    finally:
        session.close()


def test_search_finds_matching_notes_case_insensitively(tmp_path) -> None:
    repository, session = build_repository(tmp_path)

    try:
        repository.add("Buy Milk")
        repository.add("Walk the dog")
        repository.add("Remember milk for coffee")

        notes = repository.search("milk")

        assert len(notes) == 2
        assert notes[0].text == "Remember milk for coffee"
        assert notes[1].text == "Buy Milk"
    finally:
        session.close()


def test_search_respects_limit(tmp_path) -> None:
    repository, session = build_repository(tmp_path)

    try:
        repository.add("milk one")
        repository.add("milk two")
        repository.add("milk three")

        notes = repository.search("milk", limit=2)

        assert len(notes) == 2
        assert notes[0].text == "milk three"
        assert notes[1].text == "milk two"
    finally:
        session.close()