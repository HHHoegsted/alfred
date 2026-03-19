from pathlib import Path

import alfred.commands.fact as fact_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_fact_add_records_household_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "add",
            "--subject",
            "Water shutoff valve",
            "--value",
            "Under kitchen sink",
            "--details",
            "Turn clockwise to close",
        ],
    )

    assert result.exit_code == 0
    assert "Household fact recorded." in result.stdout

    service = original_build_household_fact_service(data_dir=tmp_path)
    facts = service.list_recent(limit=10)

    assert len(facts) == 1
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Under kitchen sink"
    assert facts[0].details == "Turn clockwise to close"


def test_fact_add_rejects_blank_subject(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "add",
            "--subject",
            "   ",
            "--value",
            "Under kitchen sink",
        ],
    )

    assert result.exit_code != 0
    assert "Subject cannot be empty." in result.stdout


def test_fact_add_rejects_blank_value(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "add",
            "--subject",
            "Water shutoff valve",
            "--value",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Value cannot be empty." in result.stdout


def test_fact_update_updates_existing_household_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = original_build_household_fact_service(data_dir=tmp_path)
    fact = service.record(
        subject="Water shutoff valve",
        value="Under kitchen sink",
        details="Turn clockwise to close",
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "update",
            str(fact.id),
            "--value",
            "Behind utility cabinet",
            "--details",
            "Installed during kitchen renovation",
        ],
    )

    assert result.exit_code == 0
    assert "Household fact updated." in result.stdout

    refreshed_service = original_build_household_fact_service(data_dir=tmp_path)
    facts = refreshed_service.list_recent(limit=10)

    assert len(facts) == 1
    assert facts[0].id == fact.id
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Behind utility cabinet"
    assert facts[0].details == "Installed during kitchen renovation"


def test_fact_update_rejects_blank_value(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = original_build_household_fact_service(data_dir=tmp_path)
    fact = service.record(
        subject="Water shutoff valve",
        value="Under kitchen sink",
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "update",
            str(fact.id),
            "--value",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Value cannot be empty." in result.stdout


def test_fact_update_rejects_missing_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "update",
            "9999",
            "--value",
            "Behind utility cabinet",
        ],
    )

    assert result.exit_code != 0
    assert "Household fact 9999 was not found." in result.stdout


def test_fact_retire_retires_existing_household_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = original_build_household_fact_service(data_dir=tmp_path)
    fact = service.record(
        subject="Guest Wi-Fi password",
        value="OldPassword123",
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "retire",
            str(fact.id),
            "--reason",
            "Password changed after router replacement",
        ],
    )

    assert result.exit_code == 0
    assert "Household fact retired." in result.stdout

    refreshed_service = original_build_household_fact_service(data_dir=tmp_path)
    facts = refreshed_service.list_recent(limit=10)
    assert len(facts) == 0


def test_fact_retire_rejects_missing_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "fact",
            "retire",
            "9999",
            "--reason",
            "No longer true",
        ],
    )

    assert result.exit_code != 0
    assert "Household fact 9999 was not found." in result.stdout


def test_fact_list_shows_recorded_household_facts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = original_build_household_fact_service(data_dir=tmp_path)
    service.record(
        subject="Wi-Fi SSID",
        value="WorldHouseNet",
    )

    result = runner.invoke(cli.app, ["fact", "list"])

    assert result.exit_code == 0
    assert "Wi-Fi SSID" in result.stdout
    assert "WorldHouseNet" in result.stdout


def test_fact_list_shows_no_household_facts_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    result = runner.invoke(cli.app, ["fact", "list"])

    assert result.exit_code == 0
    assert "No household facts found." in result.stdout


def test_fact_list_hides_retired_household_facts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = (
        fact_commands.bootstrap.build_household_fact_service
    )

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        fact_commands.bootstrap,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = original_build_household_fact_service(data_dir=tmp_path)
    fact = service.record(
        subject="Guest Wi-Fi password",
        value="OldPassword123",
    )
    service.retire(
        fact_id=fact.id,
        reason="Password changed after router replacement",
    )

    result = runner.invoke(cli.app, ["fact", "list"])

    assert result.exit_code == 0
    assert "Guest Wi-Fi password" not in result.stdout
    assert "OldPassword123" not in result.stdout
    assert "No household facts found." in result.stdout