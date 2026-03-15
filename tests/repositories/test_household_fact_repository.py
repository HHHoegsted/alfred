from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import HouseholdFactRepository


def test_create_persists_and_returns_household_fact(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)

        fact = repository.create(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )

    assert fact.id is not None
    assert fact.created_at is not None
    assert fact.updated_at is None
    assert fact.retired_at is None
    assert fact.retired_reason is None
    assert fact.subject == "Water shutoff valve"
    assert fact.value == "Under kitchen sink"
    assert fact.details == "Turn clockwise to close"


def test_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        repository.create(
            subject="Wi-Fi SSID",
            value="WorldHouseNet",
            details=None,
        )
        repository.create(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        facts = repository.list_recent()

    assert len(facts) == 2
    assert facts[0].subject == "Water shutoff valve"
    assert facts[1].subject == "Wi-Fi SSID"


def test_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        repository.create(subject="First", value="One", details=None)
        repository.create(subject="Second", value="Two", details=None)
        repository.create(subject="Third", value="Three", details=None)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        facts = repository.list_recent(limit=2)

    assert len(facts) == 2
    assert facts[0].subject == "Third"
    assert facts[1].subject == "Second"


def test_get_by_id_returns_household_fact_when_present(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        created = repository.create(
            subject="Router location",
            value="Office shelf",
            details=None,
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        fact = repository.get_by_id(created.id)

    assert fact is not None
    assert fact.id == created.id
    assert fact.subject == "Router location"
    assert fact.value == "Office shelf"


def test_get_by_id_returns_none_when_missing(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        fact = repository.get_by_id(9999)

    assert fact is None


def test_update_changes_fact_fields_and_sets_updated_at(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        created = repository.create(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        fact = repository.get_by_id(created.id)
        assert fact is not None

        updated = repository.update(
            fact,
            value="Behind utility cabinet",
            details="Installed during kitchen renovation",
        )

    assert updated.id == created.id
    assert updated.subject == "Water shutoff valve"
    assert updated.value == "Behind utility cabinet"
    assert updated.details == "Installed during kitchen renovation"
    assert updated.updated_at is not None
    assert updated.retired_at is None
    assert updated.retired_reason is None

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        persisted = repository.get_by_id(created.id)

    assert persisted is not None
    assert persisted.value == "Behind utility cabinet"
    assert persisted.details == "Installed during kitchen renovation"
    assert persisted.updated_at is not None


def test_retire_marks_fact_retired_with_reason(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        created = repository.create(
            subject="Guest Wi-Fi password",
            value="OldPassword123",
            details=None,
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        fact = repository.get_by_id(created.id)
        assert fact is not None

        retired = repository.retire(
            fact,
            reason="Password changed after router replacement",
        )

    assert retired.id == created.id
    assert retired.retired_at is not None
    assert retired.retired_reason == "Password changed after router replacement"

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        persisted = repository.get_by_id(created.id)

    assert persisted is not None
    assert persisted.retired_at is not None
    assert persisted.retired_reason == "Password changed after router replacement"


def test_list_recent_excludes_retired_facts(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        active_fact = repository.create(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details=None,
        )
        active_fact_id = active_fact.id

        retired_fact = repository.create(
            subject="Guest Wi-Fi password",
            value="OldPassword123",
            details=None,
        )
        repository.retire(
            retired_fact,
            reason="Password changed after router replacement",
        )

    with session_factory.get_session() as session:
        repository = HouseholdFactRepository(session)
        facts = repository.list_recent()

    assert len(facts) == 1
    assert facts[0].id == active_fact_id
    assert facts[0].subject == "Water shutoff valve"