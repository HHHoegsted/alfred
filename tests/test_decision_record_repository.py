from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import DecisionRecordRepository


def test_create_persists_and_returns_decision_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)

        record = repository.create(
            summary="Use SQLAlchemy for new structured domains",
            reason="It provides a typed persistence foundation and keeps a later Postgres move easier.",
        )

    assert record.id is not None
    assert record.created_at is not None
    assert record.summary == "Use SQLAlchemy for new structured domains"
    assert (
        record.reason
        == "It provides a typed persistence foundation and keeps a later Postgres move easier."
    )


def test_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        repository.create(summary="First decision", reason="First reason")
        repository.create(summary="Second decision", reason="Second reason")

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        records = repository.list_recent()

    assert len(records) == 2
    assert records[0].summary == "Second decision"
    assert records[1].summary == "First decision"


def test_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        repository.create(summary="First decision", reason="First reason")
        repository.create(summary="Second decision", reason="Second reason")
        repository.create(summary="Third decision", reason="Third reason")

    with session_factory.get_session() as session:
        repository = DecisionRecordRepository(session)
        records = repository.list_recent(limit=2)

    assert len(records) == 2
    assert records[0].summary == "Third decision"
    assert records[1].summary == "Second decision"