from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository
from alfred.services import PersonService


def test_person_service_register_saves_person(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    person = service.register(
        name="Sara",
        is_household_member=True,
    )

    assert person.id is not None
    assert person.name == "Sara"
    assert person.is_household_member is True

    people = service.list_recent(limit=10)
    assert len(people) == 1
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True


def test_person_service_register_strips_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    person = service.register(
        name="  Sara  ",
        is_household_member=True,
    )

    assert person.name == "Sara"


def test_person_service_register_rejects_empty_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    with pytest.raises(ValueError, match="Person name cannot be empty."):
        service.register(
            name="   ",
            is_household_member=True,
        )


def test_person_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    service.register(
        name="HH",
        is_household_member=True,
    )
    service.register(
        name="Guest",
        is_household_member=False,
    )

    people = service.list_recent(limit=10)

    assert len(people) == 2
    assert people[0].name == "Guest"
    assert people[1].name == "HH"


def test_person_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    service.register(
        name="HH",
        is_household_member=True,
    )
    service.register(
        name="Sara",
        is_household_member=True,
    )
    service.register(
        name="Guest",
        is_household_member=False,
    )

    people = service.list_recent(limit=2)

    assert len(people) == 2