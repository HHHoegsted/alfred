from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import MaintenanceRecordRepository
from alfred.services import MaintenanceRecordService


def test_maintenance_record_service_record_saves_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter and checked the drain well.",
            category="Appliance",
            notes="Filter had a small amount of debris buildup.",
        )

        assert maintenance_record.id is not None
        assert maintenance_record.subject == "Dishwasher filter cleaning"
        assert maintenance_record.performed_at.isoformat() == "2026-04-05T10:30:00"
        assert (
            maintenance_record.details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert maintenance_record.category == "Appliance"
        assert maintenance_record.notes == "Filter had a small amount of debris buildup."

        maintenance_records = service.list_recent(limit=10)
        assert len(maintenance_records) == 1
        assert maintenance_records[0].subject == "Dishwasher filter cleaning"
        assert maintenance_records[0].performed_at.isoformat() == "2026-04-05T10:30:00"
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


def test_maintenance_record_service_record_rejects_empty_subject(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(ValueError, match="Subject cannot be empty."):
            service.record(
                subject="   ",
                performed_at="2026-04-05T10:30:00",
                details="Removed and rinsed the filter and checked the drain well.",
                category="Appliance",
                notes="Filter had a small amount of debris buildup.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_record_rejects_empty_performed_at(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Performed-at timestamp cannot be empty.",
        ):
            service.record(
                subject="Dishwasher filter cleaning",
                performed_at="   ",
                details="Removed and rinsed the filter and checked the drain well.",
                category="Appliance",
                notes="Filter had a small amount of debris buildup.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_record_rejects_invalid_performed_at(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Performed-at timestamp must be a valid ISO 8601 datetime.",
        ):
            service.record(
                subject="Dishwasher filter cleaning",
                performed_at="not-a-datetime",
                details="Removed and rinsed the filter and checked the drain well.",
                category="Appliance",
                notes="Filter had a small amount of debris buildup.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_record_rejects_empty_details(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(ValueError, match="Details cannot be empty."):
            service.record(
                subject="Dishwasher filter cleaning",
                performed_at="2026-04-05T10:30:00",
                details="   ",
                category="Appliance",
                notes="Filter had a small amount of debris buildup.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_record_strips_inputs(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="  Dishwasher filter cleaning  ",
            performed_at="  2026-04-05T10:30:00  ",
            details="  Removed and rinsed the filter and checked the drain well.  ",
            category="  Appliance  ",
            notes="  Filter had a small amount of debris buildup.  ",
        )

        assert maintenance_record.subject == "Dishwasher filter cleaning"
        assert maintenance_record.performed_at.isoformat() == "2026-04-05T10:30:00"
        assert (
            maintenance_record.details
            == "Removed and rinsed the filter and checked the drain well."
        )
        assert maintenance_record.category == "Appliance"
        assert maintenance_record.notes == "Filter had a small amount of debris buildup."
    finally:
        session_factory.close()


def test_maintenance_record_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter and checked the drain well.",
            category="   ",
            notes="   ",
        )

        assert maintenance_record.category is None
        assert maintenance_record.notes is None
    finally:
        session_factory.close()


def test_maintenance_record_service_update_updates_existing_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        updated_maintenance_record = service.update(
            maintenance_record_id=maintenance_record.id,
            performed_at="2026-04-06T08:15:00",
            details="Removed, rinsed, and reinstalled the filter.",
            category="Kitchen appliance",
            notes="No damage found.",
        )

        assert updated_maintenance_record.id == maintenance_record.id
        assert updated_maintenance_record.subject == "Dishwasher filter cleaning"
        assert (
            updated_maintenance_record.performed_at.isoformat()
            == "2026-04-06T08:15:00"
        )
        assert (
            updated_maintenance_record.details
            == "Removed, rinsed, and reinstalled the filter."
        )
        assert updated_maintenance_record.category == "Kitchen appliance"
        assert updated_maintenance_record.notes == "No damage found."
        assert updated_maintenance_record.updated_at is not None
    finally:
        session_factory.close()


def test_maintenance_record_service_update_rejects_missing_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Maintenance record 9999 was not found.",
        ):
            service.update(
                maintenance_record_id=9999,
                performed_at="2026-04-06T08:15:00",
                details="Removed, rinsed, and reinstalled the filter.",
                category="Kitchen appliance",
                notes="No damage found.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_update_rejects_retired_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-05T10:30:00",
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )
        service.retire(
            maintenance_record_id=maintenance_record.id,
            reason="Replaced by a more complete maintenance log entry",
        )

        with pytest.raises(
            ValueError,
            match=(
                f"Maintenance record {maintenance_record.id} is retired "
                "and cannot be updated."
            ),
        ):
            service.update(
                maintenance_record_id=maintenance_record.id,
                performed_at="2026-04-06T08:15:00",
                details="Updated maintenance details.",
                category="HVAC",
                notes=None,
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_update_rejects_empty_performed_at(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        with pytest.raises(
            ValueError,
            match="Performed-at timestamp cannot be empty.",
        ):
            service.update(
                maintenance_record_id=maintenance_record.id,
                performed_at="   ",
                details="Removed, rinsed, and reinstalled the filter.",
                category="Kitchen appliance",
                notes="No damage found.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_update_rejects_invalid_performed_at(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        with pytest.raises(
            ValueError,
            match="Performed-at timestamp must be a valid ISO 8601 datetime.",
        ):
            service.update(
                maintenance_record_id=maintenance_record.id,
                performed_at="not-a-datetime",
                details="Removed, rinsed, and reinstalled the filter.",
                category="Kitchen appliance",
                notes="No damage found.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_update_rejects_empty_details(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        with pytest.raises(ValueError, match="Details cannot be empty."):
            service.update(
                maintenance_record_id=maintenance_record.id,
                performed_at="2026-04-06T08:15:00",
                details="   ",
                category="Kitchen appliance",
                notes="No damage found.",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_update_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        updated_maintenance_record = service.update(
            maintenance_record_id=maintenance_record.id,
            performed_at="2026-04-06T08:15:00",
            details="Removed, rinsed, and reinstalled the filter.",
            category="   ",
            notes="   ",
        )

        assert updated_maintenance_record.category is None
        assert updated_maintenance_record.notes is None
    finally:
        session_factory.close()


def test_maintenance_record_service_retire_retires_existing_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-05T10:30:00",
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )

        retired_maintenance_record = service.retire(
            maintenance_record_id=maintenance_record.id,
            reason="Replaced by a more complete maintenance log entry",
        )

        assert retired_maintenance_record.id == maintenance_record.id
        assert retired_maintenance_record.retired_at is not None
        assert (
            retired_maintenance_record.retired_reason
            == "Replaced by a more complete maintenance log entry"
        )

        maintenance_records = service.list_recent(limit=10)
        assert len(maintenance_records) == 0
    finally:
        session_factory.close()


def test_maintenance_record_service_retire_rejects_missing_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        with pytest.raises(
            ValueError,
            match="Maintenance record 9999 was not found.",
        ):
            service.retire(
                maintenance_record_id=9999,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_retire_rejects_already_retired_maintenance_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-05T10:30:00",
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )
        service.retire(
            maintenance_record_id=maintenance_record.id,
            reason="Replaced by a more complete maintenance log entry",
        )

        with pytest.raises(
            ValueError,
            match=f"Maintenance record {maintenance_record.id} is already retired.",
        ):
            service.retire(
                maintenance_record_id=maintenance_record.id,
                reason="No longer active",
            )
    finally:
        session_factory.close()


def test_maintenance_record_service_retire_normalizes_blank_reason_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        maintenance_record = service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-05T10:30:00",
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes=None,
        )

        retired_maintenance_record = service.retire(
            maintenance_record_id=maintenance_record.id,
            reason="   ",
        )

        assert retired_maintenance_record.retired_at is not None
        assert retired_maintenance_record.retired_reason is None
    finally:
        session_factory.close()


def test_maintenance_record_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        service.record(
            subject="Older maintenance",
            performed_at="2026-04-01T09:00:00",
            details="Older maintenance details.",
            category=None,
            notes=None,
        )
        service.record(
            subject="Newer maintenance",
            performed_at="2026-04-02T09:00:00",
            details="Newer maintenance details.",
            category=None,
            notes=None,
        )

        maintenance_records = service.list_recent(limit=10)

        assert len(maintenance_records) == 2
        assert maintenance_records[0].subject == "Newer maintenance"
        assert maintenance_records[1].subject == "Older maintenance"
    finally:
        session_factory.close()


def test_maintenance_record_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        service.record(
            subject="First maintenance",
            performed_at="2026-04-01T09:00:00",
            details="First maintenance details.",
            category=None,
            notes=None,
        )
        service.record(
            subject="Second maintenance",
            performed_at="2026-04-02T09:00:00",
            details="Second maintenance details.",
            category=None,
            notes=None,
        )
        service.record(
            subject="Third maintenance",
            performed_at="2026-04-03T09:00:00",
            details="Third maintenance details.",
            category=None,
            notes=None,
        )

        maintenance_records = service.list_recent(limit=2)

        assert len(maintenance_records) == 2
        assert maintenance_records[0].subject == "Third maintenance"
        assert maintenance_records[1].subject == "Second maintenance"
    finally:
        session_factory.close()


def test_maintenance_record_service_list_recent_uses_default_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = MaintenanceRecordRepository(session_factory)
    service = MaintenanceRecordService(repository)

    try:
        for index in range(12):
            service.record(
                subject=f"Maintenance {index}",
                performed_at=f"2026-04-{index + 1:02d}T09:00:00",
                details=f"Maintenance details {index}.",
                category=None,
                notes=None,
            )

        maintenance_records = service.list_recent()

        assert len(maintenance_records) == 10
        assert maintenance_records[0].subject == "Maintenance 11"
        assert maintenance_records[-1].subject == "Maintenance 2"
    finally:
        session_factory.close()
