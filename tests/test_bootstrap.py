from pathlib import Path
import sqlite3

from alfred.bootstrap import build_decision_record_service, init_sqlalchemy


def test_init_sqlalchemy_creates_decision_records_table(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    assert session_factory is not None

    db_path = tmp_path / "alfred.db"
    assert db_path.exists()

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'decision_records'
            """
        ).fetchone()

    assert row is not None
    assert row[0] == "decision_records"


def test_build_decision_record_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_decision_record_service(data_dir=tmp_path)

    created = service.record(
        summary="Keep Alfred local-first",
        reason="It matches the vision and keeps household knowledge portable.",
    )

    assert created.id is not None
    assert created.created_at is not None
    assert created.summary == "Keep Alfred local-first"
    assert (
        created.reason
        == "It matches the vision and keeps household knowledge portable."
    )

    records = service.list_recent()

    assert len(records) == 1
    assert records[0].summary == "Keep Alfred local-first"