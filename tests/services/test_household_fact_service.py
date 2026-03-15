from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import HouseholdFactRepository
from alfred.services.household_fact_service import HouseholdFactService


def test_record_creates_household_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        fact = service.record(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )

    assert fact.id is not None
    assert fact.subject == "Water shutoff valve"
    assert fact.value == "Under kitchen sink"
    assert fact.details == "Turn clockwise to close"


def test_record_trims_fields_and_normalizes_blank_details(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        fact = service.record(
            subject="  Wi-Fi SSID  ",
            value="  WorldHouseNet  ",
            details="   ",
        )

    assert fact.subject == "Wi-Fi SSID"
    assert fact.value == "WorldHouseNet"
    assert fact.details is None


def test_record_rejects_blank_subject(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(ValueError, match="Subject cannot be empty."):
            service.record(subject="   ", value="Under kitchen sink")


def test_record_rejects_blank_value(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(ValueError, match="Value cannot be empty."):
            service.record(subject="Water shutoff valve", value="   ")


def test_list_recent_returns_household_facts(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        service.record(subject="First", value="One")
        service.record(subject="Second", value="Two")

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        facts = service.list_recent()

    assert len(facts) == 2
    assert facts[0].subject == "Second"
    assert facts[1].subject == "First"