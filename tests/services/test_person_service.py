from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository
from alfred.services import PersonService


def test_person_service_register_creates_person(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        service = PersonService(repository)
        person = service.register(
            name="Sara",
            is_household_member=True,
        )

    assert person.id is not None
    assert person.name == "Sara"
    assert person.is_household_member is True
    assert person.created_at is not None

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        people = repository.list_recent()

    assert len(people) == 1
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True


def test_person_service_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        service = PersonService(repository)
        service.register(name="HH", is_household_member=True)
        service.register(name="Guest", is_household_member=False)

    with session_factory.get_session() as session:
        repository = PersonRepository(session)
        service = PersonService(repository)
        people = service.list_recent()

    assert len(people) == 2
    assert people[0].name == "Guest"
    assert people[0].is_household_member is False
    assert people[1].name == "HH"
    assert people[1].is_household_member is True