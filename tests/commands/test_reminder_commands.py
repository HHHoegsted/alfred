from pathlib import Path

import alfred.commands.reminders as reminder_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_reminder_add_records_reminder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "reminder",
            "add",
            "--title",
            "Replace smoke alarm batteries",
            "--cadence",
            "Twice a year",
            "--details",
            "Check all alarms in the house and replace batteries as needed.",
        ],
    )

    assert result.exit_code == 0
    assert "Reminder recorded." in result.stdout
    assert "[1] Replace smoke alarm batteries" in result.stdout

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        reminders = service.list_recent(limit=10)

        assert len(reminders) == 1
        assert reminders[0].title == "Replace smoke alarm batteries"
        assert reminders[0].cadence == "Twice a year"
        assert (
            reminders[0].details
            == "Check all alarms in the house and replace batteries as needed."
        )
    finally:
        service.repository.session_factory.close()


def test_reminder_add_rejects_blank_title(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "reminder",
            "add",
            "--title",
            "   ",
            "--cadence",
            "Twice a year",
            "--details",
            "Check all alarms in the house and replace batteries as needed.",
        ],
    )

    assert result.exit_code != 0
    assert "Title cannot be empty." in result.stdout


def test_reminder_update_updates_existing_reminder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        result = runner.invoke(
            cli.app,
            [
                "reminder",
                "update",
                str(reminder.id),
                "--cadence",
                "Every 6 months",
                "--details",
                "Check all alarms and test them after replacing batteries.",
            ],
        )

        assert result.exit_code == 0
        assert "Reminder updated." in result.stdout
        assert f"[{reminder.id}] Replace smoke alarm batteries" in result.stdout
    finally:
        service.repository.session_factory.close()

    refreshed_service = original_build_reminder_service(data_dir=tmp_path)
    try:
        reminders = refreshed_service.list_recent(limit=10)

        assert len(reminders) == 1
        assert reminders[0].id == reminder.id
        assert reminders[0].title == "Replace smoke alarm batteries"
        assert reminders[0].cadence == "Every 6 months"
        assert (
            reminders[0].details
            == "Check all alarms and test them after replacing batteries."
        )
    finally:
        refreshed_service.repository.session_factory.close()


def test_reminder_update_rejects_missing_reminder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "reminder",
            "update",
            "9999",
            "--cadence",
            "Every 6 months",
            "--details",
            "Check all alarms and test them after replacing batteries.",
        ],
    )

    assert result.exit_code != 0
    assert "Reminder 9999 was not found." in result.stdout


def test_reminder_retire_retires_existing_reminder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        reminder = service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )

        result = runner.invoke(
            cli.app,
            [
                "reminder",
                "retire",
                str(reminder.id),
                "--reason",
                "No longer needed after installing wired alarms",
            ],
        )

        assert result.exit_code == 0
        assert "Reminder retired." in result.stdout
        assert f"[{reminder.id}] Replace smoke alarm batteries" in result.stdout
    finally:
        service.repository.session_factory.close()

    verification_service = original_build_reminder_service(data_dir=tmp_path)
    try:
        stored_reminder = verification_service.repository.get_by_id(reminder.id)
        assert stored_reminder is not None
        assert stored_reminder.retired_at is not None
        assert (
            stored_reminder.retired_reason
            == "No longer needed after installing wired alarms"
        )
    finally:
        verification_service.repository.session_factory.close()


def test_reminder_retire_rejects_missing_reminder(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "reminder",
            "retire",
            "9999",
        ],
    )

    assert result.exit_code != 0
    assert "Reminder 9999 was not found." in result.stdout


def test_reminder_list_shows_reminders(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        service.record(
            title="Clean dishwasher filter",
            cadence="Monthly",
            details="Remove the filter, rinse it, and check the drain well.",
        )

        result = runner.invoke(cli.app, ["reminder", "list"])

        assert result.exit_code == 0
        assert "Replace smoke alarm batteries" in result.stdout
        assert "Clean dishwasher filter" in result.stdout
        assert "Cadence: Twice a year" in result.stdout
        assert "Cadence: Monthly" in result.stdout
    finally:
        service.repository.session_factory.close()


def test_reminder_list_shows_no_reminders_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    result = runner.invoke(cli.app, ["reminder", "list"])

    assert result.exit_code == 0
    assert "No reminders found." in result.stdout


def test_reminder_list_respects_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        service.record(
            title="Clean dishwasher filter",
            cadence="Monthly",
            details="Remove the filter, rinse it, and check the drain well.",
        )

        result = runner.invoke(cli.app, ["reminder", "list", "--limit", "1"])

        assert result.exit_code == 0
        assert "Clean dishwasher filter" in result.stdout
        assert "Replace smoke alarm batteries" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_reminder_list_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_reminder_service = reminder_commands.bootstrap.build_reminder_service

    def build_reminder_service_for_test():
        return original_build_reminder_service(data_dir=tmp_path)

    monkeypatch.setattr(
        reminder_commands.bootstrap,
        "build_reminder_service",
        build_reminder_service_for_test,
    )

    service = original_build_reminder_service(data_dir=tmp_path)
    try:
        service.record(
            title="Replace smoke alarm batteries",
            cadence="Twice a year",
            details="Check all alarms in the house and replace batteries as needed.",
        )
        service.record(
            title="Clean dishwasher filter",
            cadence="Monthly",
            details="Remove the filter, rinse it, and check the drain well.",
        )

        result = runner.invoke(cli.app, ["reminder", "list", "-n", "1"])

        assert result.exit_code == 0
        assert "Clean dishwasher filter" in result.stdout
        assert "Replace smoke alarm batteries" not in result.stdout
    finally:
        service.repository.session_factory.close()