from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository


def test_person_repository_create_persists_person(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)

        person = repository.create(
            name="Sara",
            is_household_member=True,
        )
        person_id = person.id

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        people = repository.list_recent()

    assert len(people) == 1
    assert people[0].id == person_id
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True
    assert people[0].created_at is not None


def test_person_repository_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)

        repository.create(name="HH", is_household_member=True)
        guest = repository.create(name="Guest", is_household_member=False)
        guest_id = guest.id

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        people = repository.list_recent()

    assert len(people) == 2
    assert people[0].id == guest_id
    assert people[0].name == "Guest"
    assert people[0].is_household_member is False
    assert people[1].name == "HH"
    assert people[1].is_household_member is True


def test_person_repository_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)

        repository.create(name="HH", is_household_member=True)
        newest_person = repository.create(name="Guest", is_household_member=False)
        newest_person_id = newest_person.id

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        people = repository.list_recent(limit=1)

    assert len(people) == 1
    assert people[0].id == newest_person_id
    assert people[0].name == "Guest"
    assert people[0].is_household_member is False