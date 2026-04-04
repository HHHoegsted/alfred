from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository


def test_person_repository_create_and_list_recent(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
        created = repository.create(
            name="Sara",
            is_household_member=True,
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.name == "Sara"
        assert created.is_household_member is True

        people = repository.list_recent(limit=10)

        assert len(people) == 1
        assert people[0].id == created.id
        assert people[0].name == "Sara"
        assert people[0].is_household_member is True
    finally:
        session_factory.close()


def test_person_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
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
    finally:
        session_factory.close()


def test_person_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
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
        assert people[0].name == "Guest"
        assert people[1].name == "Sara"
    finally:
        session_factory.close()


def test_person_repository_search_returns_matching_people_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
        repository.create(
            name="Hans-Henrik",
            is_household_member=True,
        )
        repository.create(
            name="Sara",
            is_household_member=True,
        )
        repository.create(
            name="Hanne",
            is_household_member=False,
        )

        people = repository.search(query="han", limit=10)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Hanne",
            "Hans-Henrik",
        ]
    finally:
        session_factory.close()


def test_person_repository_search_is_case_insensitive(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
        repository.create(
            name="Hans-Henrik",
            is_household_member=True,
        )
        repository.create(
            name="Sara",
            is_household_member=True,
        )

        people = repository.search(query="HANS", limit=10)

        assert len(people) == 1
        assert people[0].name == "Hans-Henrik"
    finally:
        session_factory.close()


def test_person_repository_search_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
        repository.create(
            name="Hans First",
            is_household_member=False,
        )
        repository.create(
            name="Hans Second",
            is_household_member=False,
        )
        repository.create(
            name="Hans Third",
            is_household_member=True,
        )

        people = repository.search(query="Hans", limit=2)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Hans Third",
            "Hans Second",
        ]
    finally:
        session_factory.close()


def test_person_repository_search_returns_empty_list_when_no_match(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)

    try:
        repository.create(
            name="Sara",
            is_household_member=True,
        )

        people = repository.search(query="milk", limit=10)

        assert people == []
    finally:
        session_factory.close()