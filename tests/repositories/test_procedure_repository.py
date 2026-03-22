from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import Procedure
from alfred.repositories import ProcedureRepository


def test_procedure_repository_create_and_list_recent(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        created = repository.create(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.subject == "Internet is down"
        assert (
            created.procedure
            == "Check router power before restarting anything."
        )
        assert created.category == "Troubleshooting"
        assert created.details == "If only one device is affected, start there."

        procedures = repository.list_recent(limit=10)

        assert len(procedures) == 1
        assert procedures[0].id == created.id
        assert procedures[0].subject == "Internet is down"
        assert (
            procedures[0].procedure
            == "Check router power before restarting anything."
        )
        assert procedures[0].category == "Troubleshooting"
        assert procedures[0].details == "If only one device is affected, start there."
    finally:
        session_factory.close()


def test_procedure_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        repository.create(
            subject="First procedure",
            procedure="First step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Second procedure",
            procedure="Second step.",
            category=None,
            details=None,
        )

        procedures = repository.list_recent(limit=10)

        assert len(procedures) == 2
        assert procedures[0].subject == "Second procedure"
        assert procedures[1].subject == "First procedure"
    finally:
        session_factory.close()


def test_procedure_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        repository.create(
            subject="First procedure",
            procedure="First step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Second procedure",
            procedure="Second step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Third procedure",
            procedure="Third step.",
            category=None,
            details=None,
        )

        procedures = repository.list_recent(limit=2)

        assert len(procedures) == 2
        assert procedures[0].subject == "Third procedure"
        assert procedures[1].subject == "Second procedure"
    finally:
        session_factory.close()


def test_procedure_repository_update_updates_existing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        created = repository.create(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )

        updated = repository.update(
            procedure_record=created,
            procedure="Check router power, modem lights, and ISP status.",
            category="Connectivity",
            details="Restart equipment only after outage checks.",
        )

        assert updated is not None
        assert updated.id == created.id
        assert updated.subject == "Internet is down"
        assert (
            updated.procedure
            == "Check router power, modem lights, and ISP status."
        )
        assert updated.category == "Connectivity"
        assert updated.details == "Restart equipment only after outage checks."
        assert updated.updated_at is not None
    finally:
        session_factory.close()


def test_procedure_repository_update_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        created = repository.create(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(Procedure, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        updated = repository.update(
            procedure_record=created,
            procedure="Check router power, modem lights, and ISP status.",
            category="Connectivity",
            details="Restart equipment only after outage checks.",
        )

        assert updated is created
        assert updated.id == created.id
        assert (
            updated.procedure
            == "Check router power before restarting anything."
        )
        assert updated.category == "Troubleshooting"
        assert updated.details == "If only one device is affected, start there."
        assert updated.updated_at is None
    finally:
        session_factory.close()


def test_procedure_repository_retire_marks_record_as_retired(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        created = repository.create(
            subject="Water leak under sink",
            procedure="Turn off the local shutoff valve first.",
            category="Emergency",
            details=None,
        )

        retired = repository.retire(
            procedure_record=created,
            reason="Replaced by updated plumbing playbook",
        )

        assert retired is not None
        assert retired.id == created.id
        assert retired.retired_at is not None
        assert retired.retired_reason == "Replaced by updated plumbing playbook"

        procedures = repository.list_recent(limit=10)
        assert len(procedures) == 0
    finally:
        session_factory.close()


def test_procedure_repository_retire_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = ProcedureRepository(session_factory)

    try:
        created = repository.create(
            subject="Water leak under sink",
            procedure="Turn off the local shutoff valve first.",
            category="Emergency",
            details=None,
        )

        with session_factory.get_session() as session:
            persisted = session.get(Procedure, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        retired = repository.retire(
            procedure_record=created,
            reason="Replaced by updated plumbing playbook",
        )

        assert retired is created
        assert retired.id == created.id
        assert retired.retired_at is None
        assert retired.retired_reason is None
    finally:
        session_factory.close()