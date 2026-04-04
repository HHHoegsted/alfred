from datetime import datetime
from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import MaintenanceRecord
from alfred.repositories import MaintenanceRecordRepository


def test_maintenance_record_repository_create_and_list_recent(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    performed_at = datetime.fromisoformat("2026-04-05T10:30:00")

    try:
        created = repository.create(
            subject="Dishwasher filter cleaning",
            performed_at=performed_at,
            details="Removed and rinsed the filter and checked the drain well.",
            category="Appliance",
            notes="Filter had a small amount of debris buildup.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.subject == "Dishwasher filter cleaning"
        assert created.performed_at == performed_at
        assert (
            created.details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert created.category == "Appliance"
        assert created.notes == "Filter had a small amount of debris buildup."

        maintenance_records = repository.list_recent(limit=10)

        assert len(maintenance_records) == 1
        assert maintenance_records[0].id == created.id
        assert maintenance_records[0].subject == "Dishwasher filter cleaning"
        assert maintenance_records[0].performed_at == performed_at
        assert (
            maintenance_records[0].details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert maintenance_records[0].category == "Appliance"
        assert (
            maintenance_records[0].notes
            == "Filter had a small amount of debris buildup."
        )
    finally:
        session_factory.close()


def test_maintenance_record_repository_get_by_id_returns_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    performed_at = datetime.fromisoformat("2026-04-05T10:30:00")

    try:
        created = repository.create(
            subject="Dishwasher filter cleaning",
            performed_at=performed_at,
            details="Removed and rinsed the filter and checked the drain well.",
            category="Appliance",
            notes="Filter had a small amount of debris buildup.",
        )

        maintenance_record = repository.get_by_id(created.id)

        assert maintenance_record is not None
        assert maintenance_record.id == created.id
        assert maintenance_record.subject == "Dishwasher filter cleaning"
        assert maintenance_record.performed_at == performed_at
        assert (
            maintenance_record.details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert maintenance_record.category == "Appliance"
        assert maintenance_record.notes == "Filter had a small amount of debris buildup."
    finally:
        session_factory.close()


def test_maintenance_record_repository_get_by_id_returns_none_for_missing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        maintenance_record = repository.get_by_id(9999)

        assert maintenance_record is None
    finally:
        session_factory.close()


def test_maintenance_record_repository_list_recent_returns_newest_first_by_performed_at(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        repository.create(
            subject="Older maintenance",
            performed_at=datetime.fromisoformat("2026-04-01T09:00:00"),
            details="Older maintenance details.",
            category=None,
            notes=None,
        )
        repository.create(
            subject="Newer maintenance",
            performed_at=datetime.fromisoformat("2026-04-02T09:00:00"),
            details="Newer maintenance details.",
            category=None,
            notes=None,
        )

        maintenance_records = repository.list_recent(limit=10)

        assert len(maintenance_records) == 2
        assert maintenance_records[0].subject == "Newer maintenance"
        assert maintenance_records[1].subject == "Older maintenance"
    finally:
        session_factory.close()


def test_maintenance_record_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        repository.create(
            subject="First maintenance",
            performed_at=datetime.fromisoformat("2026-04-01T09:00:00"),
            details="First maintenance details.",
            category=None,
            notes=None,
        )
        repository.create(
            subject="Second maintenance",
            performed_at=datetime.fromisoformat("2026-04-02T09:00:00"),
            details="Second maintenance details.",
            category=None,
            notes=None,
        )
        repository.create(
            subject="Third maintenance",
            performed_at=datetime.fromisoformat("2026-04-03T09:00:00"),
            details="Third maintenance details.",
            category=None,
            notes=None,
        )

        maintenance_records = repository.list_recent(limit=2)

        assert len(maintenance_records) == 2
        assert maintenance_records[0].subject == "Third maintenance"
        assert maintenance_records[1].subject == "Second maintenance"
    finally:
        session_factory.close()


def test_maintenance_record_repository_update_updates_existing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        created = repository.create(
            subject="Dishwasher filter cleaning",
            performed_at=datetime.fromisoformat("2026-04-05T10:30:00"),
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        updated = repository.update(
            maintenance_record=created,
            performed_at=datetime.fromisoformat("2026-04-06T08:15:00"),
            details="Removed, rinsed, and reinstalled the filter.",
            category="Kitchen appliance",
            notes="No damage found.",
        )

        assert updated is not None
        assert updated.id == created.id
        assert updated.subject == "Dishwasher filter cleaning"
        assert updated.performed_at == datetime.fromisoformat("2026-04-06T08:15:00")
        assert updated.details == "Removed, rinsed, and reinstalled the filter."
        assert updated.category == "Kitchen appliance"
        assert updated.notes == "No damage found."
        assert updated.updated_at is not None
    finally:
        session_factory.close()


def test_maintenance_record_repository_update_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        created = repository.create(
            subject="Dishwasher filter cleaning",
            performed_at=datetime.fromisoformat("2026-04-05T10:30:00"),
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(MaintenanceRecord, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        updated = repository.update(
            maintenance_record=created,
            performed_at=datetime.fromisoformat("2026-04-06T08:15:00"),
            details="Removed, rinsed, and reinstalled the filter.",
            category="Kitchen appliance",
            notes="No damage found.",
        )

        assert updated is created
        assert updated.id == created.id
        assert updated.performed_at == datetime.fromisoformat("2026-04-05T10:30:00")
        assert updated.details == "Removed and rinsed the filter."
        assert updated.category == "Appliance"
        assert updated.notes == "Initial note."
        assert updated.updated_at is None
    finally:
        session_factory.close()


def test_maintenance_record_repository_retire_marks_record_as_retired(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        created = repository.create(
            subject="HVAC filter replacement",
            performed_at=datetime.fromisoformat("2026-04-05T10:30:00"),
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )

        retired = repository.retire(
            maintenance_record=created,
            reason="Replaced by a more complete maintenance log entry",
        )

        assert retired is not None
        assert retired.id == created.id
        assert retired.retired_at is not None
        assert (
            retired.retired_reason
            == "Replaced by a more complete maintenance log entry"
        )

        maintenance_records = repository.list_recent(limit=10)
        assert len(maintenance_records) == 0
    finally:
        session_factory.close()


def test_maintenance_record_repository_retire_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)

    try:
        created = repository.create(
            subject="HVAC filter replacement",
            performed_at=datetime.fromisoformat("2026-04-05T10:30:00"),
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )

        with session_factory.get_session() as session:
            persisted = session.get(MaintenanceRecord, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        retired = repository.retire(
            maintenance_record=created,
            reason="Replaced by a more complete maintenance log entry",
        )

        assert retired is created
        assert retired.id == created.id
        assert retired.retired_at is None
        assert retired.retired_reason is None
    finally:
        session_factory.close()