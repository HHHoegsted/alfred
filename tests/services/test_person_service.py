from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PersonRepository
from alfred.services import PersonService


def test_person_service_register_saves_person(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        person = service.register(
            name="Sara",
            is_household_member=True,
        )

        assert person.id is not None
        assert person.created_at is not None
        assert person.name == "Sara"
        assert person.is_household_member is True

        people = service.list_recent(limit=10)

        assert len(people) == 1
        assert people[0].name == "Sara"
        assert people[0].is_household_member is True
    finally:
        session_factory.close()


def test_person_service_register_rejects_empty_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        with pytest.raises(ValueError, match="Person name cannot be empty."):
            service.register(name="   ", is_household_member=False)
    finally:
        session_factory.close()


def test_person_service_register_strips_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        person = service.register(
            name="  HH  ",
            is_household_member=False,
        )

        assert person.name == "HH"
    finally:
        session_factory.close()


def test_person_service_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        service.register(name="First", is_household_member=False)
        service.register(name="Second", is_household_member=True)

        people = service.list_recent(limit=10)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Second",
            "First",
        ]
    finally:
        session_factory.close()


def test_person_service_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        service.register(name="First", is_household_member=False)
        service.register(name="Second", is_household_member=False)
        service.register(name="Third", is_household_member=True)

        people = service.list_recent(limit=2)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Third",
            "Second",
        ]
    finally:
        session_factory.close()


def test_person_service_search_returns_matching_people(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        service.register(name="Hans-Henrik", is_household_member=True)
        service.register(name="Sara", is_household_member=True)
        service.register(name="Hanne", is_household_member=False)

        people = service.search(query="han", limit=10)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Hanne",
            "Hans-Henrik",
        ]
    finally:
        session_factory.close()


def test_person_service_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        service.register(name="Hans First", is_household_member=False)
        service.register(name="Hans Second", is_household_member=False)
        service.register(name="Hans Third", is_household_member=True)

        people = service.search(query="Hans", limit=2)

        assert len(people) == 2
        assert [person.name for person in people] == [
            "Hans Third",
            "Hans Second",
        ]
    finally:
        session_factory.close()


def test_person_service_search_rejects_blank_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        with pytest.raises(ValueError, match="Search query cannot be empty."):
            service.search(query="   ", limit=10)
    finally:
        session_factory.close()


def test_person_service_search_strips_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PersonRepository(session_factory)
    service = PersonService(repository)

    try:
        service.register(name="Hans-Henrik", is_household_member=True)
        service.register(name="Sara", is_household_member=True)

        people = service.search(query="  Hans  ", limit=10)

        assert len(people) == 1
        assert people[0].name == "Hans-Henrik"
    finally:
        session_factory.close()