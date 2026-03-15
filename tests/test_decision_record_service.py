from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import DecisionRecordRepository
from alfred.services import DecisionRecordService


def test_record_creates_decision_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        record = service.record(
            summary="Use SQLAlchemy for new structured domains",
            reason="It provides a typed persistence foundation and eases a later move to Postgres.",
        )

    assert record.id is not None
    assert record.created_at is not None
    assert record.summary == "Use SQLAlchemy for new structured domains"
    assert (
        record.reason
        == "It provides a typed persistence foundation and eases a later move to Postgres."
    )


def test_record_trims_summary_and_reason(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        record = service.record(
            summary="  Keep notes local-first  ",
            reason="  Privacy and portability matter.  ",
        )

    assert record.summary == "Keep notes local-first"
    assert record.reason == "Privacy and portability matter."


def test_record_rejects_empty_summary(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        with pytest.raises(ValueError, match="Decision summary cannot be empty."):
            service.record(
                summary="   ",
                reason="A reason exists.",
            )


def test_record_rejects_empty_reason(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        with pytest.raises(ValueError, match="Decision reason cannot be empty."):
            service.record(
                summary="A summary exists.",
                reason="   ",
            )


def test_list_recent_returns_records(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        service.record(summary="First decision", reason="First reason")
        service.record(summary="Second decision", reason="Second reason")

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        service = DecisionRecordService(repository)

        records = service.list_recent()

    assert len(records) == 2
    assert records[0].summary == "Second decision"
    assert records[1].summary == "First decision"