from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import DecisionRecordRepository


def test_decision_record_repository_create_persists_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)

    record = repository.create(
        summary="Use SQLAlchemy",
        reason="Easier later move to Postgres",
    )

    assert record.id is not None
    assert record.summary == "Use SQLAlchemy"
    assert record.reason == "Easier later move to Postgres"

    records = repository.list_recent(limit=10)

    assert len(records) == 1
    assert records[0].id == record.id
    assert records[0].summary == "Use SQLAlchemy"
    assert records[0].reason == "Easier later move to Postgres"


def test_decision_record_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)

    repository.create(
        summary="First decision",
        reason="First reason",
    )
    repository.create(
        summary="Second decision",
        reason="Second reason",
    )

    records = repository.list_recent(limit=10)

    assert len(records) == 2
    assert records[0].summary == "Second decision"
    assert records[1].summary == "First decision"


def test_decision_record_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)

    repository.create(
        summary="First decision",
        reason="First reason",
    )
    repository.create(
        summary="Second decision",
        reason="Second reason",
    )
    repository.create(
        summary="Third decision",
        reason="Third reason",
    )

    records = repository.list_recent(limit=2)

    assert len(records) == 2