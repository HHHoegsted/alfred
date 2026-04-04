from pathlib import Path

import alfred.commands.maintenance_records as maintenance_record_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_maintenance_add_records_maintenance_record(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "add",
            "--subject",
            "Dishwasher filter cleaning",
            "--performed-at",
            "2026-04-05T10:30:00",
            "--details",
            "Removed and rinsed the filter and checked the drain well.",
            "--category",
            "Appliance",
            "--notes",
            "Filter had a small amount of debris buildup.",
        ],
    )

    assert result.exit_code == 0
    assert "Maintenance record recorded." in result.stdout
    assert "[1] Dishwasher filter cleaning" in result.stdout

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_records = service.list_recent(limit=10)

        assert len(maintenance_records) == 1
        assert maintenance_records[0].subject == "Dishwasher filter cleaning"
        assert (
            maintenance_records[0].performed_at.isoformat()
            == "2026-04-05T10:30:00"
        )
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
        service.repository.session_factory.close()


def test_maintenance_add_rejects_blank_subject(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "add",
            "--subject",
            "   ",
            "--performed-at",
            "2026-04-05T10:30:00",
            "--details",
            "Removed and rinsed the filter and checked the drain well.",
        ],
    )

    assert result.exit_code != 0
    assert "Subject cannot be empty." in result.stdout


def test_maintenance_add_rejects_blank_performed_at(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "add",
            "--subject",
            "Dishwasher filter cleaning",
            "--performed-at",
            "   ",
            "--details",
            "Removed and rinsed the filter and checked the drain well.",
        ],
    )

    assert result.exit_code != 0
    assert "Performed-at timestamp cannot be empty." in result.stdout


def test_maintenance_add_rejects_invalid_performed_at(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "add",
            "--subject",
            "Dishwasher filter cleaning",
            "--performed-at",
            "not-a-datetime",
            "--details",
            "Removed and rinsed the filter and checked the drain well.",
        ],
    )

    assert result.exit_code != 0
    assert "Performed-at timestamp must be a valid ISO 8601 datetime." in result.stdout


def test_maintenance_add_rejects_blank_details(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "add",
            "--subject",
            "Dishwasher filter cleaning",
            "--performed-at",
            "2026-04-05T10:30:00",
            "--details",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Details cannot be empty." in result.stdout


def test_maintenance_update_updates_existing_maintenance_record(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
            category="Appliance",
            notes="Initial note.",
        )

        result = runner.invoke(
            cli.app,
            [
                "maintenance",
                "update",
                str(maintenance_record.id),
                "--performed-at",
                "2026-04-06T08:15:00",
                "--details",
                "Removed, rinsed, and reinstalled the filter.",
                "--category",
                "Kitchen appliance",
                "--notes",
                "No damage found.",
            ],
        )

        assert result.exit_code == 0
        assert "Maintenance record updated." in result.stdout
        assert f"[{maintenance_record.id}] Dishwasher filter cleaning" in result.stdout
    finally:
        service.repository.session_factory.close()

    refreshed_service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_records = refreshed_service.list_recent(limit=10)

        assert len(maintenance_records) == 1
        assert maintenance_records[0].id == maintenance_record.id
        assert maintenance_records[0].subject == "Dishwasher filter cleaning"
        assert (
            maintenance_records[0].performed_at.isoformat()
            == "2026-04-06T08:15:00"
        )
        assert (
            maintenance_records[0].details
            == "Removed, rinsed, and reinstalled the filter."
        )
        assert maintenance_records[0].category == "Kitchen appliance"
        assert maintenance_records[0].notes == "No damage found."
    finally:
        refreshed_service.repository.session_factory.close()


def test_maintenance_update_rejects_blank_performed_at(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
        )

        result = runner.invoke(
            cli.app,
            [
                "maintenance",
                "update",
                str(maintenance_record.id),
                "--performed-at",
                "   ",
                "--details",
                "Removed, rinsed, and reinstalled the filter.",
            ],
        )

        assert result.exit_code != 0
        assert "Performed-at timestamp cannot be empty." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_maintenance_update_rejects_invalid_performed_at(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
        )

        result = runner.invoke(
            cli.app,
            [
                "maintenance",
                "update",
                str(maintenance_record.id),
                "--performed-at",
                "not-a-datetime",
                "--details",
                "Removed, rinsed, and reinstalled the filter.",
            ],
        )

        assert result.exit_code != 0
        assert "Performed-at timestamp must be a valid ISO 8601 datetime." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_maintenance_update_rejects_blank_details(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_record = service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
        )

        result = runner.invoke(
            cli.app,
            [
                "maintenance",
                "update",
                str(maintenance_record.id),
                "--performed-at",
                "2026-04-06T08:15:00",
                "--details",
                "   ",
            ],
        )

        assert result.exit_code != 0
        assert "Details cannot be empty." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_maintenance_update_rejects_missing_maintenance_record(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "update",
            "9999",
            "--performed-at",
            "2026-04-06T08:15:00",
            "--details",
            "Removed, rinsed, and reinstalled the filter.",
        ],
    )

    assert result.exit_code != 0
    assert "Maintenance record 9999 was not found." in result.stdout


def test_maintenance_retire_retires_existing_maintenance_record(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        maintenance_record = service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-05T10:30:00",
            details="Replaced the old filter with a new one.",
        )

        result = runner.invoke(
            cli.app,
            [
                "maintenance",
                "retire",
                str(maintenance_record.id),
                "--reason",
                "Replaced by a more complete maintenance log entry",
            ],
        )

        assert result.exit_code == 0
        assert "Maintenance record retired." in result.stdout
        assert f"[{maintenance_record.id}] HVAC filter replacement" in result.stdout
    finally:
        service.repository.session_factory.close()

    verification_service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        stored_maintenance_record = verification_service.repository.get_by_id(
            maintenance_record.id
        )
        assert stored_maintenance_record is not None
        assert stored_maintenance_record.retired_at is not None
        assert (
            stored_maintenance_record.retired_reason
            == "Replaced by a more complete maintenance log entry"
        )
    finally:
        verification_service.repository.session_factory.close()


def test_maintenance_retire_rejects_missing_maintenance_record(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "maintenance",
            "retire",
            "9999",
        ],
    )

    assert result.exit_code != 0
    assert "Maintenance record 9999 was not found." in result.stdout


def test_maintenance_list_shows_maintenance_records(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter and checked the drain well.",
            category="Appliance",
            notes="Filter had a small amount of debris buildup.",
        )
        service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-06T08:15:00",
            details="Replaced the old filter with a new one.",
            category="HVAC",
            notes="Used the spare filter from storage.",
        )

        result = runner.invoke(cli.app, ["maintenance", "list"])

        assert result.exit_code == 0
        assert "Dishwasher filter cleaning" in result.stdout
        assert "HVAC filter replacement" in result.stdout
        assert "Category: Appliance" in result.stdout
        assert "Category: HVAC" in result.stdout
        assert "Notes: Filter had a small amount of debris buildup." in result.stdout
        assert "Notes: Used the spare filter from storage." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_maintenance_list_shows_no_maintenance_records_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    result = runner.invoke(cli.app, ["maintenance", "list"])

    assert result.exit_code == 0
    assert "No maintenance records found." in result.stdout


def test_maintenance_list_respects_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
        )
        service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-06T08:15:00",
            details="Replaced the old filter with a new one.",
        )

        result = runner.invoke(cli.app, ["maintenance", "list", "--limit", "1"])

        assert result.exit_code == 0
        assert "HVAC filter replacement" in result.stdout
        assert "Dishwasher filter cleaning" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_maintenance_list_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_maintenance_record_service = (
        maintenance_record_commands.bootstrap.build_maintenance_record_service
    )

    def build_maintenance_record_service_for_test():
        return original_build_maintenance_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        maintenance_record_commands.bootstrap,
        "build_maintenance_record_service",
        build_maintenance_record_service_for_test,
    )

    service = original_build_maintenance_record_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Dishwasher filter cleaning",
            performed_at="2026-04-05T10:30:00",
            details="Removed and rinsed the filter.",
        )
        service.record(
            subject="HVAC filter replacement",
            performed_at="2026-04-06T08:15:00",
            details="Replaced the old filter with a new one.",
        )

        result = runner.invoke(cli.app, ["maintenance", "list", "-n", "1"])

        assert result.exit_code == 0
        assert "HVAC filter replacement" in result.stdout
        assert "Dishwasher filter cleaning" not in result.stdout
    finally:
        service.repository.session_factory.close()