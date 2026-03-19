from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import HouseholdFactRepository
from alfred.services import HouseholdFactService


def test_household_fact_service_record_saves_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
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

    facts = service.list_recent(limit=10)
    assert len(facts) == 1
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Under kitchen sink"
    assert facts[0].details == "Turn clockwise to close"


def test_household_fact_service_record_rejects_empty_subject(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    with pytest.raises(ValueError, match="Subject cannot be empty."):
        service.record(
            subject="   ",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )


def test_household_fact_service_record_rejects_empty_value(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    with pytest.raises(ValueError, match="Value cannot be empty."):
        service.record(
            subject="Water shutoff valve",
            value="   ",
            details="Turn clockwise to close",
        )


def test_household_fact_service_record_strips_inputs(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    fact = service.record(
        subject="  Water shutoff valve  ",
        value="  Under kitchen sink  ",
        details="  Turn clockwise to close  ",
    )

    assert fact.subject == "Water shutoff valve"
    assert fact.value == "Under kitchen sink"
    assert fact.details == "Turn clockwise to close"


def test_household_fact_service_update_updates_existing_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    fact = service.record(
        subject="Water shutoff valve",
        value="Under kitchen sink",
        details="Turn clockwise to close",
    )

    updated_fact = service.update(
        fact_id=fact.id,
        value="Behind utility cabinet",
        details="Installed during kitchen renovation",
    )

    assert updated_fact.id == fact.id
    assert updated_fact.subject == "Water shutoff valve"
    assert updated_fact.value == "Behind utility cabinet"
    assert updated_fact.details == "Installed during kitchen renovation"
    assert updated_fact.updated_at is not None


def test_household_fact_service_update_rejects_missing_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    with pytest.raises(ValueError, match="Household fact 9999 was not found."):
        service.update(
            fact_id=9999,
            value="Behind utility cabinet",
            details="Installed during kitchen renovation",
        )


def test_household_fact_service_retire_retires_existing_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    fact = service.record(
        subject="Guest Wi-Fi password",
        value="OldPassword123",
        details=None,
    )

    retired_fact = service.retire(
        fact_id=fact.id,
        reason="Password changed after router replacement",
    )

    assert retired_fact.id == fact.id
    assert retired_fact.retired_at is not None
    assert retired_fact.retired_reason == "Password changed after router replacement"

    facts = service.list_recent(limit=10)
    assert len(facts) == 0


def test_household_fact_service_retire_rejects_missing_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    with pytest.raises(ValueError, match="Household fact 9999 was not found."):
        service.retire(
            fact_id=9999,
            reason="No longer true",
        )


def test_household_fact_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    service.record(
        subject="First fact",
        value="First value",
        details=None,
    )
    service.record(
        subject="Second fact",
        value="Second value",
        details=None,
    )

    facts = service.list_recent(limit=10)

    assert len(facts) == 2
    assert facts[0].subject == "Second fact"
    assert facts[1].subject == "First fact"


def test_household_fact_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    service.record(
        subject="First fact",
        value="First value",
        details=None,
    )
    service.record(
        subject="Second fact",
        value="Second value",
        details=None,
    )
    service.record(
        subject="Third fact",
        value="Third value",
        details=None,
    )

    facts = service.list_recent(limit=2)

    assert len(facts) == 2