from pathlib import Path

from alfred.bootstrap import build_household_fact_service
from alfred.repositories import HouseholdFactRepository


def build_household_fact_repository(tmp_path: Path) -> HouseholdFactRepository:
    service = build_household_fact_service(data_dir=tmp_path)
    return service.repository


def test_create_stores_household_fact(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)

    fact = repository.create(
        subject="Water shutoff valve",
        value="Under kitchen sink",
        details="Turn clockwise to close",
    )

    assert fact.id is not None
    assert fact.subject == "Water shutoff valve"
    assert fact.value == "Under kitchen sink"
    assert fact.details == "Turn clockwise to close"


def test_get_by_id_returns_household_fact(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)
    created_fact = repository.create(
        subject="Fuse box",
        value="Utility room",
        details="Label inside door",
    )

    fact = repository.get_by_id(created_fact.id)

    assert fact is not None
    assert fact.id == created_fact.id
    assert fact.subject == "Fuse box"


def test_get_by_id_returns_none_for_missing_household_fact(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)

    fact = repository.get_by_id(999)

    assert fact is None


def test_update_changes_value_and_details(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)
    fact = repository.create(
        subject="Wi-Fi router",
        value="Office shelf",
        details="Behind the monitor",
    )

    updated_fact = repository.update(
        fact,
        value="Hall cupboard",
        details="Moved during cleanup",
    )

    assert updated_fact.id == fact.id
    assert updated_fact.subject == "Wi-Fi router"
    assert updated_fact.value == "Hall cupboard"
    assert updated_fact.details == "Moved during cleanup"
    assert updated_fact.updated_at is not None


def test_retire_sets_retired_fields(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)
    fact = repository.create(
        subject="Spare key",
        value="Top drawer",
        details=None,
    )

    retired_fact = repository.retire(
        fact,
        reason="No longer stored there",
    )

    assert retired_fact.id == fact.id
    assert retired_fact.retired_at is not None
    assert retired_fact.retired_reason == "No longer stored there"


def test_list_recent_returns_non_retired_facts_newest_first(tmp_path: Path) -> None:
    repository = build_household_fact_repository(tmp_path)

    first_fact = repository.create(
        subject="Old fact",
        value="Old value",
        details=None,
    )
    second_fact = repository.create(
        subject="New fact",
        value="New value",
        details=None,
    )

    repository.retire(first_fact, reason="Outdated")

    facts = repository.list_recent()

    assert [fact.id for fact in facts] == [second_fact.id]