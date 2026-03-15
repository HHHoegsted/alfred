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


def test_update_changes_value_and_details(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )
        created_id = created.id

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        updated = service.update(
            fact_id=created_id,
            value="  Behind utility cabinet  ",
            details="  Installed during kitchen renovation  ",
        )

    assert updated.id == created_id
    assert updated.subject == "Water shutoff valve"
    assert updated.value == "Behind utility cabinet"
    assert updated.details == "Installed during kitchen renovation"
    assert updated.updated_at is not None
    assert updated.retired_at is None
    assert updated.retired_reason is None


def test_update_normalizes_blank_details_to_none(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Router location",
            value="Office shelf",
            details="Top shelf",
        )
        created_id = created.id

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        updated = service.update(
            fact_id=created_id,
            value="Hall closet",
            details="   ",
        )

    assert updated.value == "Hall closet"
    assert updated.details is None


def test_update_rejects_blank_value(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Router location",
            value="Office shelf",
        )
        created_id = created.id

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(ValueError, match="Value cannot be empty."):
            service.update(
                fact_id=created_id,
                value="   ",
                details="Still in the same place",
            )


def test_update_rejects_missing_fact_id(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(ValueError, match="Household fact 9999 was not found."):
            service.update(
                fact_id=9999,
                value="New value",
                details=None,
            )


def test_retire_marks_fact_retired(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Guest Wi-Fi password",
            value="OldPassword123",
        )
        created_id = created.id

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        retired = service.retire(
            fact_id=created_id,
            reason="  Password changed after router replacement  ",
        )

    assert retired.id == created_id
    assert retired.retired_at is not None
    assert retired.retired_reason == "Password changed after router replacement"


def test_retire_normalizes_blank_reason_to_none(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Temporary door code",
            value="1234",
        )
        created_id = created.id

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        retired = service.retire(
            fact_id=created_id,
            reason="   ",
        )

    assert retired.retired_at is not None
    assert retired.retired_reason is None


def test_retire_rejects_missing_fact_id(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(ValueError, match="Household fact 9999 was not found."):
            service.retire(
                fact_id=9999,
                reason="No longer true",
            )


def test_update_rejects_retired_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Guest Wi-Fi password",
            value="OldPassword123",
        )
        created_id = created.id
        service.retire(
            fact_id=created_id,
            reason="Password changed after router replacement",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(
            ValueError,
            match=f"Household fact {created_id} is retired and cannot be updated.",
        ):
            service.update(
                fact_id=created_id,
                value="NewPassword456",
                details=None,
            )


def test_retire_rejects_already_retired_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        created = service.record(
            subject="Temporary alarm code",
            value="2468",
        )
        created_id = created.id
        service.retire(
            fact_id=created_id,
            reason="Expired after contractor visit",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)

        with pytest.raises(
            ValueError,
            match=f"Household fact {created_id} is already retired.",
        ):
            service.retire(
                fact_id=created_id,
                reason="Still retired",
            )


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


def test_list_recent_excludes_retired_household_facts(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        service.record(subject="Active fact", value="Keep me")
        retired = service.record(subject="Retired fact", value="Hide me")
        service.retire(
            fact_id=retired.id,
            reason="No longer true",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        service = HouseholdFactService(repository)
        facts = service.list_recent()

    assert len(facts) == 1
    assert facts[0].subject == "Active fact"