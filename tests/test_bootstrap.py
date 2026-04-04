from pathlib import Path
import sqlite3

from alfred.bootstrap import (
    build_care_instruction_service,
    build_decision_record_service,
    build_maintenance_record_service,
    build_person_service,
    build_procedure_service,
    build_reminder_service,
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


def test_init_sqlalchemy_creates_maintenance_records_table(tmp_path: Path) -> None:
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
                WHERE type = 'table' AND name = 'maintenance_records'
                """
            ).fetchone()
        finally:
            connection.close()

        assert row is not None
        assert row[0] == "maintenance_records"
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_reminders_table(tmp_path: Path) -> None:
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
                WHERE type = 'table' AND name = 'reminders'
                """
            ).fetchone()
        finally:
            connection.close()

        assert row is not None
        assert row[0] == "reminders"
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


def test_build_maintenance_record_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_maintenance_record_service(data_dir=tmp_path)

    try:
        created = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter and checked the drain well.",
            category="Appliance",
            notes="Filter had a small amount of debris buildup.",
        )
        maintenance_records = service.list_recent()

        created_id = created.id
        created_at = created.created_at
        created_subject = created.subject
        created_performed_at = created.performed_at
        created_details = created.details
        created_category = created.category
        created_notes = created.notes

        assert created_id is not None
        assert created_at is not None
        assert created_subject == "Dishwasher filter cleaning"
        assert created_performed_at.isoformat() == "2026-04-05T10:30:00"
        assert (
            created_details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert created_category == "Appliance"
        assert created_notes == "Filter had a small amount of debris buildup."

        assert len(maintenance_records) == 1
        assert maintenance_records[0].subject == "Dishwasher filter cleaning"
        assert (
            maintenance_records[0].performed_at.isoformat()
            == "2026-04-05T10:30:00"
        )
    finally:
        service.repository.session_factory.close()


def test_build_reminder_service_returns_working_service(
    tmp_path: Path,
) -> None:
    service = build_reminder_service(data_dir=tmp_path)

    try:
        created = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        reminders = service.list_recent()

        created_id = created.id
        created_at = created.created_at
        created_title = created.title
        created_cadence = created.cadence
        created_details = created.details

        assert created_id is not None
        assert created_at is not None
        assert created_title == "Replace smoke alarm batteries"
        assert created_cadence == "Twice a year"
        assert (
            created_details
            == "Check all alarms in the house and replace batteries as needed."
        )

        assert len(reminders) == 1
        assert reminders[0].title == "Replace smoke alarm batteries"
        assert reminders[0].cadence == "Twice a year"
    finally:
        service.repository.session_factory.close()