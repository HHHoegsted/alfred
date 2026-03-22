from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import HouseholdFactRepository
from alfred.services import HouseholdFactService


def test_household_fact_service_record_saves_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        assert fact.id is not None
        assert fact.subject == "Wi-Fi password"
        assert fact.value == "CorrectHorseBatteryStaple"
        assert fact.details == "Main household network password."

        facts = service.list_recent(limit=10)
        assert len(facts) == 1
        assert facts[0].subject == "Wi-Fi password"
        assert facts[0].value == "CorrectHorseBatteryStaple"
        assert facts[0].details == "Main household network password."
    finally:
        session_factory.close()


def test_household_fact_service_record_rejects_empty_subject(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        with pytest.raises(ValueError, match="Subject cannot be empty."):
            service.record(
                subject="   ",
                value="CorrectHorseBatteryStaple",
                details="Main household network password.",
            )
    finally:
        session_factory.close()


def test_household_fact_service_record_rejects_empty_value(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        with pytest.raises(ValueError, match="Value cannot be empty."):
            service.record(
                subject="Wi-Fi password",
                value="   ",
                details="Main household network password.",
            )
    finally:
        session_factory.close()


def test_household_fact_service_record_strips_inputs(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="  Wi-Fi password  ",
            value="  CorrectHorseBatteryStaple  ",
            details="  Main household network password.  ",
        )

        assert fact.subject == "Wi-Fi password"
        assert fact.value == "CorrectHorseBatteryStaple"
        assert fact.details == "Main household network password."
    finally:
        session_factory.close()


def test_household_fact_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="   ",
        )

        assert fact.details is None
    finally:
        session_factory.close()


def test_household_fact_service_update_updates_existing_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        updated_fact = service.update(
            fact_id=fact.id,
            value="HorseBatteryStapleCorrect",
            details="Updated after router reset.",
        )

        assert updated_fact.id == fact.id
        assert updated_fact.subject == "Wi-Fi password"
        assert updated_fact.value == "HorseBatteryStapleCorrect"
        assert updated_fact.details == "Updated after router reset."
        assert updated_fact.updated_at is not None
    finally:
        session_factory.close()


def test_household_fact_service_update_rejects_missing_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Household fact 9999 was not found.",
        ):
            service.update(
                fact_id=9999,
                value="HorseBatteryStapleCorrect",
                details="Updated after router reset.",
            )
    finally:
        session_factory.close()


def test_household_fact_service_update_rejects_retired_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )
        service.retire(fact_id=fact.id)

        with pytest.raises(
            ValueError,
            match=f"Household fact {fact.id} is retired and cannot be updated.",
        ):
            service.update(
                fact_id=fact.id,
                value="HorseBatteryStapleCorrect",
                details="Updated after router reset.",
            )
    finally:
        session_factory.close()


def test_household_fact_service_update_rejects_empty_value(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        with pytest.raises(ValueError, match="Value cannot be empty."):
            service.update(
                fact_id=fact.id,
                value="   ",
                details="Updated after router reset.",
            )
    finally:
        session_factory.close()


def test_household_fact_service_update_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        updated_fact = service.update(
            fact_id=fact.id,
            value="HorseBatteryStapleCorrect",
            details="   ",
        )

        assert updated_fact.details is None
    finally:
        session_factory.close()


def test_household_fact_service_retire_retires_existing_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Alarm code",
            value="1234",
            details=None,
        )

        retired_fact = service.retire(
            fact_id=fact.id,
            reason="Replaced by new alarm panel",
        )

        assert retired_fact.id == fact.id
        assert retired_fact.retired_at is not None
        assert retired_fact.retired_reason == "Replaced by new alarm panel"

        facts = service.list_recent(limit=10)
        assert len(facts) == 0
    finally:
        session_factory.close()


def test_household_fact_service_retire_rejects_missing_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Household fact 9999 was not found.",
        ):
            service.retire(
                fact_id=9999,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_household_fact_service_retire_rejects_already_retired_fact(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Alarm code",
            value="1234",
            details=None,
        )
        service.retire(
            fact_id=fact.id,
            reason="Replaced by new alarm panel",
        )

        with pytest.raises(
            ValueError,
            match=f"Household fact {fact.id} is already retired.",
        ):
            service.retire(
                fact_id=fact.id,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_household_fact_service_retire_normalizes_blank_reason_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
        fact = service.record(
            subject="Alarm code",
            value="1234",
            details=None,
        )

        retired_fact = service.retire(
            fact_id=fact.id,
            reason="   ",
        )

        assert retired_fact.retired_at is not None
        assert retired_fact.retired_reason is None
    finally:
        session_factory.close()


def test_household_fact_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
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
    finally:
        session_factory.close()


def test_household_fact_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)
    service = HouseholdFactService(repository)

    try:
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
        assert facts[0].subject == "Third fact"
        assert facts[1].subject == "Second fact"
    finally:
        session_factory.close()