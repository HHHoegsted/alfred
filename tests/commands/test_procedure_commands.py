from pathlib import Path

import alfred.commands.procedures as procedure_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_procedure_add_records_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "procedure",
            "add",
            "--subject",
            "Internet is down",
            "--procedure",
            "Check router power before restarting anything.",
            "--category",
            "Troubleshooting",
            "--details",
            "If only one device is affected, start there.",
        ],
    )

    assert result.exit_code == 0
    assert "Procedure recorded." in result.stdout
    assert "[1] Internet is down" in result.stdout

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        procedures = service.list_recent(limit=10)

        assert len(procedures) == 1
        assert procedures[0].subject == "Internet is down"
        assert (
            procedures[0].procedure
            == "Check router power before restarting anything."
        )
        assert procedures[0].category == "Troubleshooting"
        assert procedures[0].details == "If only one device is affected, start there."
    finally:
        service.repository.session_factory.close()


def test_procedure_add_rejects_blank_subject(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "procedure",
            "add",
            "--subject",
            "   ",
            "--procedure",
            "Check router power before restarting anything.",
        ],
    )

    assert result.exit_code != 0
    assert "Subject cannot be empty." in result.stdout


def test_procedure_add_rejects_blank_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "procedure",
            "add",
            "--subject",
            "Internet is down",
            "--procedure",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Procedure cannot be empty." in result.stdout


def test_procedure_update_updates_existing_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        procedure_record = service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )

        result = runner.invoke(
            cli.app,
            [
                "procedure",
                "update",
                str(procedure_record.id),
                "--procedure",
                "Check router power, then modem lights, then ISP status.",
                "--category",
                "Connectivity",
                "--details",
                "Restart equipment only after checking outage status.",
            ],
        )

        assert result.exit_code == 0
        assert "Procedure updated." in result.stdout
        assert f"[{procedure_record.id}] Internet is down" in result.stdout
    finally:
        service.repository.session_factory.close()

    refreshed_service = original_build_procedure_service(data_dir=tmp_path)
    try:
        procedures = refreshed_service.list_recent(limit=10)

        assert len(procedures) == 1
        assert procedures[0].id == procedure_record.id
        assert procedures[0].subject == "Internet is down"
        assert (
            procedures[0].procedure
            == "Check router power, then modem lights, then ISP status."
        )
        assert procedures[0].category == "Connectivity"
        assert (
            procedures[0].details
            == "Restart equipment only after checking outage status."
        )
    finally:
        refreshed_service.repository.session_factory.close()


def test_procedure_update_rejects_blank_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        procedure_record = service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
        )

        result = runner.invoke(
            cli.app,
            [
                "procedure",
                "update",
                str(procedure_record.id),
                "--procedure",
                "   ",
            ],
        )

        assert result.exit_code != 0
        assert "Procedure cannot be empty." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_procedure_update_rejects_missing_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "procedure",
            "update",
            "9999",
            "--procedure",
            "Check router power, then modem lights, then ISP status.",
        ],
    )

    assert result.exit_code != 0
    assert "Procedure 9999 was not found." in result.stdout


def test_procedure_retire_retires_existing_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        procedure_record = service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
        )

        result = runner.invoke(
            cli.app,
            [
                "procedure",
                "retire",
                str(procedure_record.id),
                "--reason",
                "Replaced by updated home network playbook.",
            ],
        )

        assert result.exit_code == 0
        assert "Procedure retired." in result.stdout
        assert f"[{procedure_record.id}] Internet is down" in result.stdout
    finally:
        service.repository.session_factory.close()

    verification_service = original_build_procedure_service(data_dir=tmp_path)
    try:
        stored_procedure = verification_service.repository.get_by_id(
            procedure_record.id
        )
        assert stored_procedure is not None
        assert stored_procedure.retired_at is not None
        assert (
            stored_procedure.retired_reason
            == "Replaced by updated home network playbook."
        )
    finally:
        verification_service.repository.session_factory.close()


def test_procedure_retire_rejects_missing_procedure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "procedure",
            "retire",
            "9999",
        ],
    )

    assert result.exit_code != 0
    assert "Procedure 9999 was not found." in result.stdout


def test_procedure_list_shows_procedures(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
            category="Troubleshooting",
            details="If only one device is affected, start there.",
        )
        service.record(
            subject="Water leak under sink",
            procedure="Turn off the local shutoff valve first.",
            category="Emergency",
            details="Keep towels in the under-sink drawer.",
        )

        result = runner.invoke(cli.app, ["procedure", "list"])

        assert result.exit_code == 0
        assert "Internet is down" in result.stdout
        assert "Water leak under sink" in result.stdout
        assert "Category: Troubleshooting" in result.stdout
        assert "Category: Emergency" in result.stdout
    finally:
        service.repository.session_factory.close()


def test_procedure_list_shows_no_procedures_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    result = runner.invoke(cli.app, ["procedure", "list"])

    assert result.exit_code == 0
    assert "No procedures found." in result.stdout


def test_procedure_list_respects_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
        )
        service.record(
            subject="Water leak under sink",
            procedure="Turn off the local shutoff valve first.",
        )

        result = runner.invoke(cli.app, ["procedure", "list", "--limit", "1"])

        assert result.exit_code == 0
        assert "Water leak under sink" in result.stdout
        assert "Internet is down" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_procedure_list_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_procedure_service = (
        procedure_commands.bootstrap.build_procedure_service
    )

    def build_procedure_service_for_test():
        return original_build_procedure_service(data_dir=tmp_path)

    monkeypatch.setattr(
        procedure_commands.bootstrap,
        "build_procedure_service",
        build_procedure_service_for_test,
    )

    service = original_build_procedure_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Internet is down",
            procedure="Check router power before restarting anything.",
        )
        service.record(
            subject="Water leak under sink",
            procedure="Turn off the local shutoff valve first.",
        )

        result = runner.invoke(cli.app, ["procedure", "list", "-n", "1"])

        assert result.exit_code == 0
        assert "Water leak under sink" in result.stdout
        assert "Internet is down" not in result.stdout
    finally:
        service.repository.session_factory.close()