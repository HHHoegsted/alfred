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