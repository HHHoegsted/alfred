from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import ProcedureRepository


def test_create_saves_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    procedure_record = repository.create(
        subject="Internet is down",
        category="Troubleshooting",
        procedure="Check router power before restarting anything.",
        details="If only one device is affected, start there.",
    )

    assert procedure_record.id is not None
    assert procedure_record.subject == "Internet is down"
    assert procedure_record.category == "Troubleshooting"
    assert (
        procedure_record.procedure
        == "Check router power before restarting anything."
    )
    assert procedure_record.details == "If only one device is affected, start there."
    assert procedure_record.created_at is not None
    assert procedure_record.updated_at is None
    assert procedure_record.retired_at is None
    assert procedure_record.retired_reason is None


def test_get_by_id_returns_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    created = repository.create(
        subject="Water leak under sink",
        category="Emergency",
        procedure="Turn off the local shutoff valve first.",
        details="Keep towels in the under-sink drawer.",
    )

    fetched = repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.subject == "Water leak under sink"
    assert fetched.category == "Emergency"
    assert fetched.procedure == "Turn off the local shutoff valve first."
    assert fetched.details == "Keep towels in the under-sink drawer."


def test_get_by_id_returns_none_when_missing(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    fetched = repository.get_by_id(9999)

    assert fetched is None


def test_update_updates_existing_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    created = repository.create(
        subject="Internet is down",
        category="Troubleshooting",
        procedure="Check router power before restarting anything.",
        details="If only one device is affected, start there.",
    )

    updated = repository.update(
        created,
        category="Connectivity",
        procedure="Check router power, modem lights, and ISP status.",
        details="Restart equipment only after outage checks.",
    )

    assert updated.id == created.id
    assert updated.subject == "Internet is down"
    assert updated.category == "Connectivity"
    assert (
        updated.procedure
        == "Check router power, modem lights, and ISP status."
    )
    assert updated.details == "Restart equipment only after outage checks."
    assert updated.updated_at is not None

    fetched = repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.category == "Connectivity"
    assert fetched.procedure == "Check router power, modem lights, and ISP status."
    assert fetched.details == "Restart equipment only after outage checks."
    assert fetched.updated_at is not None


def test_retire_marks_procedure_as_retired(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    created = repository.create(
        subject="Water leak under sink",
        category="Emergency",
        procedure="Turn off the local shutoff valve first.",
        details=None,
    )

    retired = repository.retire(
        created,
        reason="Replaced by updated plumbing playbook.",
    )

    assert retired.id == created.id
    assert retired.retired_at is not None
    assert retired.retired_reason == "Replaced by updated plumbing playbook."

    fetched = repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.retired_at is not None
    assert fetched.retired_reason == "Replaced by updated plumbing playbook."


def test_list_recent_returns_only_active_procedures_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    first = repository.create(
        subject="First procedure",
        category=None,
        procedure="First step.",
        details=None,
    )
    second = repository.create(
        subject="Second procedure",
        category=None,
        procedure="Second step.",
        details=None,
    )
    third = repository.create(
        subject="Third procedure",
        category=None,
        procedure="Third step.",
        details=None,
    )

    repository.retire(
        second,
        reason="No longer relevant.",
    )

    procedures = repository.list_recent(limit=10)

    assert [procedure.id for procedure in procedures] == [
        third.id,
        first.id,
    ]


def test_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    repository.create(
        subject="First procedure",
        category=None,
        procedure="First step.",
        details=None,
    )
    second = repository.create(
        subject="Second procedure",
        category=None,
        procedure="Second step.",
        details=None,
    )
    third = repository.create(
        subject="Third procedure",
        category=None,
        procedure="Third step.",
        details=None,
    )

    procedures = repository.list_recent(limit=2)

    assert len(procedures) == 2
    assert [procedure.id for procedure in procedures] == [
        third.id,
        second.id,
    ]