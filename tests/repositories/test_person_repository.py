from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository


def test_person_repository_create_persists_person(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    person = repository.create(
        name="Sara",
        is_household_member=True,
    )

    assert person.id is not None
    assert person.name == "Sara"
    assert person.is_household_member is True

    people = repository.list_recent(limit=10)

    assert len(people) == 1
    assert people[0].id == person.id
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True


def test_person_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    repository.create(
        name="HH",
        is_household_member=True,
    )
    repository.create(
        name="Guest",
        is_household_member=False,
    )

    people = repository.list_recent(limit=10)

    assert len(people) == 2
    assert people[0].name == "Guest"
    assert people[1].name == "HH"


def test_person_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    repository.create(
        name="HH",
        is_household_member=True,
    )
    repository.create(
        name="Sara",
        is_household_member=True,
    )
    repository.create(
        name="Guest",
        is_household_member=False,
    )

    people = repository.list_recent(limit=2)

    assert len(people) == 2