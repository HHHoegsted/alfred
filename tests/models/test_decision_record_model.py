from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import DecisionRecord


def test_decision_record_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        record = DecisionRecord(
            summary="Use SQLAlchemy for new structured domains",
            reason="It gives Alfred a typed persistence foundation and eases a later move to Postgres",
        )
        session.add(record)
        session.commit()

    with session_factory.get_session() as session:
        records = session.query(DecisionRecord).all()

    assert len(records) == 1
    assert records[0].summary == "Use SQLAlchemy for new structured domains"
    assert (
        records[0].reason
        == "It gives Alfred a typed persistence foundation and eases a later move to Postgres"
    )
    assert records[0].id is not None
    assert records[0].created_at is not None