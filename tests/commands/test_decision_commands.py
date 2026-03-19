from pathlib import Path

import alfred.commands.decisions as decision_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_decision_record_records_decision(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_decision_record_service = (
        decision_commands.bootstrap.build_decision_record_service
    )

    def build_decision_record_service_for_test():
        return original_build_decision_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        decision_commands.bootstrap,
        "build_decision_record_service",
        build_decision_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "decision",
            "record",
            "--summary",
            "Use Home Assistant for house orchestration",
            "--reason",
            "It provides a stable integration point for Alfred",
        ],
    )

    assert result.exit_code == 0
    assert "Decision recorded." in result.stdout
    assert "Use Home Assistant for house orchestration" in result.stdout

    service = original_build_decision_record_service(data_dir=tmp_path)
    records = service.list_recent(limit=10)

    assert len(records) == 1
    assert records[0].summary == "Use Home Assistant for house orchestration"
    assert records[0].reason == "It provides a stable integration point for Alfred"


def test_decision_record_rejects_blank_summary(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_decision_record_service = (
        decision_commands.bootstrap.build_decision_record_service
    )

    def build_decision_record_service_for_test():
        return original_build_decision_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        decision_commands.bootstrap,
        "build_decision_record_service",
        build_decision_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "decision",
            "record",
            "--summary",
            "   ",
            "--reason",
            "It provides a stable integration point for Alfred",
        ],
    )

    assert result.exit_code != 0
    assert "Decision summary cannot be empty." in result.stdout


def test_decision_record_rejects_blank_reason(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_decision_record_service = (
        decision_commands.bootstrap.build_decision_record_service
    )

    def build_decision_record_service_for_test():
        return original_build_decision_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        decision_commands.bootstrap,
        "build_decision_record_service",
        build_decision_record_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "decision",
            "record",
            "--summary",
            "Use Home Assistant for house orchestration",
            "--reason",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Decision reason cannot be empty." in result.stdout


def test_decision_list_shows_recorded_decisions(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_decision_record_service = (
        decision_commands.bootstrap.build_decision_record_service
    )

    def build_decision_record_service_for_test():
        return original_build_decision_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        decision_commands.bootstrap,
        "build_decision_record_service",
        build_decision_record_service_for_test,
    )

    service = original_build_decision_record_service(data_dir=tmp_path)
    service.record(
        summary="Use Home Assistant for house orchestration",
        reason="It provides a stable integration point for Alfred",
    )

    result = runner.invoke(cli.app, ["decision", "list"])

    assert result.exit_code == 0
    assert "Use Home Assistant for house orchestration" in result.stdout
    assert "It provides a stable integration point for Alfred" in result.stdout


def test_decision_list_shows_no_decision_records_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_decision_record_service = (
        decision_commands.bootstrap.build_decision_record_service
    )

    def build_decision_record_service_for_test():
        return original_build_decision_record_service(data_dir=tmp_path)

    monkeypatch.setattr(
        decision_commands.bootstrap,
        "build_decision_record_service",
        build_decision_record_service_for_test,
    )

    result = runner.invoke(cli.app, ["decision", "list"])

    assert result.exit_code == 0
    assert "No decision records found." in result.stdout