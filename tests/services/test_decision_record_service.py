from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import DecisionRecordRepository
from alfred.services import DecisionRecordService


def test_decision_record_service_record_saves_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    record = service.record(
        summary="Use SQLAlchemy",
        reason="Easier later move to Postgres",
    )

    assert record.id is not None
    assert record.summary == "Use SQLAlchemy"
    assert record.reason == "Easier later move to Postgres"

    records = service.list_recent(limit=10)
    assert len(records) == 1
    assert records[0].summary == "Use SQLAlchemy"
    assert records[0].reason == "Easier later move to Postgres"


def test_decision_record_service_record_rejects_empty_summary(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    with pytest.raises(ValueError, match="Decision summary cannot be empty."):
        service.record(
            summary="   ",
            reason="Easier later move to Postgres",
        )


def test_decision_record_service_record_rejects_empty_reason(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    with pytest.raises(ValueError, match="Decision reason cannot be empty."):
        service.record(
            summary="Use SQLAlchemy",
            reason="   ",
        )


def test_decision_record_service_record_strips_inputs(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    record = service.record(
        summary="  Use SQLAlchemy  ",
        reason="  Easier later move to Postgres  ",
    )

    assert record.summary == "Use SQLAlchemy"
    assert record.reason == "Easier later move to Postgres"


def test_decision_record_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    service.record(
        summary="First decision",
        reason="First reason",
    )
    service.record(
        summary="Second decision",
        reason="Second reason",
    )

    records = service.list_recent(limit=10)

    assert len(records) == 2
    assert records[0].summary == "Second decision"
    assert records[1].summary == "First decision"


def test_decision_record_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = DecisionRecordRepository(session_factory)
    service = DecisionRecordService(repository)

    service.record(
        summary="First decision",
        reason="First reason",
    )
    service.record(
        summary="Second decision",
        reason="Second reason",
    )
    service.record(
        summary="Third decision",
        reason="Third reason",
    )

    records = service.list_recent(limit=2)

    assert len(records) == 2