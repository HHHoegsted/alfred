from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import ProcedureRepository
from alfred.services import ProcedureService


def test_procedure_service_record_saves_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Unplug power for 30 seconds, then reconnect.",
            details="Used for the living room router.",
        )

        assert procedure_record.id is not None
        assert procedure_record.subject == "Reset router"
        assert procedure_record.category == "network"
        assert procedure_record.procedure == (
            "Unplug power for 30 seconds, then reconnect."
        )
        assert procedure_record.details == "Used for the living room router."

        saved_records = service.list_recent(limit=10)
        assert len(saved_records) == 1
        assert saved_records[0].subject == "Reset router"
    finally:
        session_factory.close()


def test_procedure_service_record_strips_and_normalizes_blank_optionals(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="  Reset router  ",
            category="   ",
            procedure="  Unplug power for 30 seconds, then reconnect.  ",
            details="   ",
        )

        assert procedure_record.subject == "Reset router"
        assert procedure_record.category is None
        assert procedure_record.procedure == (
            "Unplug power for 30 seconds, then reconnect."
        )
        assert procedure_record.details is None
    finally:
        session_factory.close()


def test_procedure_service_record_rejects_empty_subject(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        with pytest.raises(ValueError, match="Subject cannot be empty."):
            service.record(
                subject="   ",
                category="network",
                procedure="Unplug power for 30 seconds, then reconnect.",
                details="Used for the living room router.",
            )
    finally:
        session_factory.close()


def test_procedure_service_record_rejects_empty_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        with pytest.raises(ValueError, match="Procedure cannot be empty."):
            service.record(
                subject="Reset router",
                category="network",
                procedure="   ",
                details="Used for the living room router.",
            )
    finally:
        session_factory.close()


def test_procedure_service_update_updates_existing_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Old procedure.",
            details="Old details.",
        )

        updated_record = service.update(
            procedure_id=procedure_record.id,
            category="hardware",
            procedure="Power off for 60 seconds, then reconnect.",
            details="Applies to the office router.",
        )

        assert updated_record.id == procedure_record.id
        assert updated_record.subject == "Reset router"
        assert updated_record.category == "hardware"
        assert updated_record.procedure == "Power off for 60 seconds, then reconnect."
        assert updated_record.details == "Applies to the office router."
        assert updated_record.updated_at is not None
    finally:
        session_factory.close()


def test_procedure_service_update_normalizes_blank_optionals_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Old procedure.",
            details="Old details.",
        )

        updated_record = service.update(
            procedure_id=procedure_record.id,
            category="   ",
            procedure="  New procedure.  ",
            details="   ",
        )

        assert updated_record.category is None
        assert updated_record.procedure == "New procedure."
        assert updated_record.details is None
    finally:
        session_factory.close()


def test_procedure_service_update_rejects_missing_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        with pytest.raises(ValueError, match="Procedure 999 was not found."):
            service.update(
                procedure_id=999,
                category="network",
                procedure="Updated procedure.",
                details="Updated details.",
            )
    finally:
        session_factory.close()


def test_procedure_service_update_rejects_retired_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Original procedure.",
            details="Original details.",
        )
        service.retire(procedure_record.id, reason="Replaced by a newer process.")

        with pytest.raises(
            ValueError,
            match=f"Procedure {procedure_record.id} is retired and cannot be updated.",
        ):
            service.update(
                procedure_id=procedure_record.id,
                category="hardware",
                procedure="Updated procedure.",
                details="Updated details.",
            )
    finally:
        session_factory.close()


def test_procedure_service_update_rejects_empty_procedure(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Original procedure.",
            details="Original details.",
        )

        with pytest.raises(ValueError, match="Procedure cannot be empty."):
            service.update(
                procedure_id=procedure_record.id,
                category="hardware",
                procedure="   ",
                details="Updated details.",
            )
    finally:
        session_factory.close()


def test_procedure_service_retire_marks_record_as_retired(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Original procedure.",
            details="Original details.",
        )

        retired_record = service.retire(
            procedure_record.id,
            reason="  Replaced by a newer process.  ",
        )

        assert retired_record.id == procedure_record.id
        assert retired_record.retired_at is not None
        assert retired_record.retired_reason == "Replaced by a newer process."
    finally:
        session_factory.close()


def test_procedure_service_retire_normalizes_blank_reason_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Original procedure.",
            details="Original details.",
        )

        retired_record = service.retire(
            procedure_record.id,
            reason="   ",
        )

        assert retired_record.retired_at is not None
        assert retired_record.retired_reason is None
    finally:
        session_factory.close()


def test_procedure_service_retire_rejects_missing_record(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        with pytest.raises(ValueError, match="Procedure 999 was not found."):
            service.retire(999, reason="No longer needed.")
    finally:
        session_factory.close()


def test_procedure_service_retire_rejects_already_retired_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        procedure_record = service.record(
            subject="Reset router",
            category="network",
            procedure="Original procedure.",
            details="Original details.",
        )
        service.retire(procedure_record.id, reason="No longer needed.")

        with pytest.raises(
            ValueError,
            match=f"Procedure {procedure_record.id} is already retired.",
        ):
            service.retire(procedure_record.id, reason="Still no longer needed.")
    finally:
        session_factory.close()


def test_procedure_service_list_recent_excludes_retired_and_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)
    service = ProcedureService(repository)

    try:
        first_record = service.record(
            subject="First procedure",
            category="general",
            procedure="First steps.",
            details=None,
        )
        service.record(
            subject="Second procedure",
            category="general",
            procedure="Second steps.",
            details=None,
        )
        service.record(
            subject="Third procedure",
            category="general",
            procedure="Third steps.",
            details=None,
        )

        service.retire(first_record.id, reason="Obsolete.")

        records = service.list_recent(limit=2)

        assert len(records) == 2
        assert records[0].subject == "Third procedure"
        assert records[1].subject == "Second procedure"
    finally:
        session_factory.close()