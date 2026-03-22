from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import ProcedureRepository
from alfred.services import ProcedureService


def test_procedure_service_record_saves_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    procedure_record = service.record(
        subject="Internet is down",
        procedure="Check router power before restarting anything.",
        category="Troubleshooting",
        details="If only one device is affected, start there.",
    )

    assert procedure_record.id is not None
    assert procedure_record.subject == "Internet is down"
    assert (
        procedure_record.procedure
        == "Check router power before restarting anything."
    )
    assert procedure_record.category == "Troubleshooting"
    assert (
        procedure_record.details
        == "If only one device is affected, start there."
    )

    procedures = service.list_recent(limit=10)
    assert len(procedures) == 1
    assert procedures[0].subject == "Internet is down"
    assert (
        procedures[0].procedure
        == "Check router power before restarting anything."
    )
    assert procedures[0].category == "Troubleshooting"
    assert procedures[0].details == "If only one device is affected, start there."


def test_procedure_service_record_rejects_empty_subject(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    with pytest.raises(ValueError, match="Subject cannot be empty."):
        service.record(
            subject="   ",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )


def test_procedure_service_record_rejects_empty_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    with pytest.raises(ValueError, match="Procedure cannot be empty."):
        service.record(
            subject="Internet is down",
            procedure="   ",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )


def test_procedure_service_record_strips_inputs(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    procedure_record = service.record(
        subject="  Internet is down  ",
        procedure="  Check router power before restarting anything.  ",
        category="  Troubleshooting  ",
        details="  If only one device is affected, start there.  ",
    )

    assert procedure_record.subject == "Internet is down"
    assert (
        procedure_record.procedure
        == "Check router power before restarting anything."
    )
    assert procedure_record.category == "Troubleshooting"
    assert procedure_record.details == "If only one device is affected, start there."


def test_procedure_service_update_updates_existing_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    procedure_record = service.record(
        subject="Internet is down",
        procedure="Check router power before restarting anything.",
        category="Troubleshooting",
        details="If only one device is affected, start there.",
    )

    updated_procedure = service.update(
        procedure_id=procedure_record.id,
        procedure="Check router power, modem lights, and ISP status.",
        category="Connectivity",
        details="Restart equipment only after outage checks.",
    )

    assert updated_procedure.id == procedure_record.id
    assert updated_procedure.subject == "Internet is down"
    assert (
        updated_procedure.procedure
        == "Check router power, modem lights, and ISP status."
    )
    assert updated_procedure.category == "Connectivity"
    assert updated_procedure.details == "Restart equipment only after outage checks."
    assert updated_procedure.updated_at is not None


def test_procedure_service_update_rejects_missing_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    with pytest.raises(
        ValueError,
        match="Procedure 9999 was not found.",
    ):
        service.update(
            procedure_id=9999,
            procedure="Check router power, modem lights, and ISP status.",
            category="Connectivity",
            details="Restart equipment only after outage checks.",
        )


def test_procedure_service_retire_retires_existing_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    procedure_record = service.record(
        subject="Water leak under sink",
        procedure="Turn off the local shutoff valve first.",
        category="Emergency",
        details=None,
    )

    retired_procedure = service.retire(
        procedure_id=procedure_record.id,
        reason="Replaced by updated plumbing playbook",
    )

    assert retired_procedure.id == procedure_record.id
    assert retired_procedure.retired_at is not None
    assert (
        retired_procedure.retired_reason
        == "Replaced by updated plumbing playbook"
    )

    procedures = service.list_recent(limit=10)
    assert len(procedures) == 0


def test_procedure_service_retire_rejects_missing_procedure(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    with pytest.raises(
        ValueError,
        match="Procedure 9999 was not found.",
    ):
        service.retire(
            procedure_id=9999,
            reason="No longer active",
        )


def test_procedure_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    service.record(
        subject="First procedure",
        procedure="First step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Second procedure",
        procedure="Second step.",
        category=None,
        details=None,
    )

    procedures = service.list_recent(limit=10)

    assert len(procedures) == 2
    assert procedures[0].subject == "Second procedure"
    assert procedures[1].subject == "First procedure"


def test_procedure_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    service.record(
        subject="First procedure",
        procedure="First step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Second procedure",
        procedure="Second step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Third procedure",
        procedure="Third step.",
        category=None,
        details=None,
    )

    procedures = service.list_recent(limit=2)

    assert len(procedures) == 2
    assert procedures[0].subject == "Third procedure"
    assert procedures[1].subject == "Second procedure"