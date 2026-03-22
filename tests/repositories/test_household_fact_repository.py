from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import HouseholdFact
from alfred.repositories import HouseholdFactRepository


def test_household_fact_repository_create_and_list_recent(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.subject == "Wi-Fi password"
        assert created.value == "CorrectHorseBatteryStaple"
        assert created.details == "Main household network password."

        facts = repository.list_recent(limit=10)

        assert len(facts) == 1
        assert facts[0].id == created.id
        assert facts[0].subject == "Wi-Fi password"
        assert facts[0].value == "CorrectHorseBatteryStaple"
        assert facts[0].details == "Main household network password."
    finally:
        session_factory.close()


def test_household_fact_repository_get_by_id_returns_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        fact = repository.get_by_id(created.id)

        assert fact is not None
        assert fact.id == created.id
        assert fact.subject == "Wi-Fi password"
        assert fact.value == "CorrectHorseBatteryStaple"
        assert fact.details == "Main household network password."
    finally:
        session_factory.close()


def test_household_fact_repository_get_by_id_returns_none_for_missing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        fact = repository.get_by_id(9999)

        assert fact is None
    finally:
        session_factory.close()


def test_household_fact_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        repository.create(
            subject="First fact",
            value="First value",
            details=None,
        )
        repository.create(
            subject="Second fact",
            value="Second value",
            details=None,
        )

        facts = repository.list_recent(limit=10)

        assert len(facts) == 2
        assert facts[0].subject == "Second fact"
        assert facts[1].subject == "First fact"
    finally:
        session_factory.close()


def test_household_fact_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        repository.create(
            subject="First fact",
            value="First value",
            details=None,
        )
        repository.create(
            subject="Second fact",
            value="Second value",
            details=None,
        )
        repository.create(
            subject="Third fact",
            value="Third value",
            details=None,
        )

        facts = repository.list_recent(limit=2)

        assert len(facts) == 2
        assert facts[0].subject == "Third fact"
        assert facts[1].subject == "Second fact"
    finally:
        session_factory.close()


def test_household_fact_repository_update_updates_existing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        updated = repository.update(
            fact=created,
            value="HorseBatteryStapleCorrect",
            details="Updated after router reset.",
        )

        assert updated is not None
        assert updated.id == created.id
        assert updated.subject == "Wi-Fi password"
        assert updated.value == "HorseBatteryStapleCorrect"
        assert updated.details == "Updated after router reset."
        assert updated.updated_at is not None
    finally:
        session_factory.close()


def test_household_fact_repository_update_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Wi-Fi password",
            value="CorrectHorseBatteryStaple",
            details="Main household network password.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(HouseholdFact, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        updated = repository.update(
            fact=created,
            value="HorseBatteryStapleCorrect",
            details="Updated after router reset.",
        )

        assert updated is created
        assert updated.id == created.id
        assert updated.value == "CorrectHorseBatteryStaple"
        assert updated.details == "Main household network password."
    finally:
        session_factory.close()


def test_household_fact_repository_retire_marks_record_as_retired(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Alarm code",
            value="1234",
            details=None,
        )

        retired = repository.retire(
            fact=created,
            reason="Replaced by new alarm panel",
        )

        assert retired is not None
        assert retired.id == created.id
        assert retired.retired_at is not None
        assert retired.retired_reason == "Replaced by new alarm panel"

        facts = repository.list_recent(limit=10)
        assert len(facts) == 0
    finally:
        session_factory.close()


def test_household_fact_repository_retire_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = HouseholdFactRepository(session_factory)

    try:
        created = repository.create(
            subject="Alarm code",
            value="1234",
            details=None,
        )

        with session_factory.get_session() as session:
            persisted = session.get(HouseholdFact, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        retired = repository.retire(
            fact=created,
            reason="Replaced by new alarm panel",
        )

        assert retired is created
        assert retired.id == created.id
        assert retired.retired_at is None
        assert retired.retired_reason is None
    finally:
        session_factory.close()