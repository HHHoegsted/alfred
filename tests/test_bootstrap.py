from pathlib import Path
import sqlite3

from alfred.bootstrap import (
    build_care_instruction_service,
    build_decision_record_service,
    build_person_service,
    build_procedure_service,
    init_sqlalchemy,
)


def test_init_sqlalchemy_creates_decision_records_table(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        assert session_factory is not None

        db_path = tmp_path / "alfred.db"
        assert db_path.exists()

        connection = sqlite3.connect(db_path)
        try:
            row = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'decision_records'
                """
            ).fetchone()
        finally:
            connection.close()

        assert row is not None
        assert row[0] == "decision_records"
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_care_instructions_table(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        assert session_factory is not None

        db_path = tmp_path / "alfred.db"
        assert db_path.exists()

        connection = sqlite3.connect(db_path)
        try:
            row = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'care_instructions'
                """
            ).fetchone()
        finally:
            connection.close()

        assert row is not None
        assert row[0] == "care_instructions"
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_procedures_table(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        assert session_factory is not None

        db_path = tmp_path / "alfred.db"
        assert db_path.exists()

        connection = sqlite3.connect(db_path)
        try:
            row = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'procedures'
                """
            ).fetchone()
        finally:
            connection.close()

        assert row is not None
        assert row[0] == "procedures"
    finally:
        session_factory.close()


def test_build_decision_record_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_decision_record_service(data_dir=tmp_path)

    try:
        created = service.record(
            summary="Keep Alfred local-first",
            reason="It matches the vision and keeps household knowledge portable.",
        )
        records = service.list_recent()

        created_id = created.id
        created_at = created.created_at
        created_summary = created.summary
        created_reason = created.reason

        assert created_id is not None
        assert created_at is not None
        assert created_summary == "Keep Alfred local-first"
        assert (
            created_reason
            == "It matches the vision and keeps household knowledge portable."
        )

        assert len(records) == 1
        assert records[0].summary == "Keep Alfred local-first"
    finally:
        service.repository.session_factory.close()


def test_build_person_service_returns_working_service(tmp_path: Path) -> None:
    service = build_person_service(data_dir=tmp_path)

    try:
        created = service.register(
            name="Sara",
            is_household_member=True,
        )
        people = service.list_recent()

        created_id = created.id
        created_name = created.name
        created_is_household_member = created.is_household_member

        assert created_id is not None
        assert created_name == "Sara"
        assert created_is_household_member is True

        assert len(people) == 1
        assert people[0].name == "Sara"
        assert people[0].is_household_member is True
    finally:
        service.repository.session_factory.close()


def test_build_care_instruction_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_care_instruction_service(data_dir=tmp_path)

    try:
        created = service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )
        care_instructions = service.list_recent()

        created_id = created.id
        created_at = created.created_at
        created_subject = created.subject
        created_instruction = created.instruction
        created_category = created.category
        created_details = created.details

        assert created_id is not None
        assert created_at is not None
        assert created_subject == "Wool blanket"
        assert created_instruction == "Wash on wool cycle with cold water."
        assert created_category == "Cleaning"
        assert created_details == "Air dry flat to avoid stretching."

        assert len(care_instructions) == 1
        assert care_instructions[0].subject == "Wool blanket"
        assert (
            care_instructions[0].instruction
            == "Wash on wool cycle with cold water."
        )
    finally:
        service.repository.session_factory.close()


def test_build_procedure_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_procedure_service(data_dir=tmp_path)

    try:
        created = service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )
        procedures = service.list_recent()

        created_id = created.id
        created_at = created.created_at
        created_subject = created.subject
        created_procedure = created.procedure
        created_category = created.category
        created_details = created.details

        assert created_id is not None
        assert created_at is not None
        assert created_subject == "Internet is down"
        assert created_procedure == "Check router power before restarting anything."
        assert created_category == "Troubleshooting"
        assert created_details == "If only one device is affected, start there."

        assert len(procedures) == 1
        assert procedures[0].subject == "Internet is down"
        assert (
            procedures[0].procedure
            == "Check router power before restarting anything."
        )
    finally:
        service.repository.session_factory.close()