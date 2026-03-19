from pathlib import Path

import alfred.commands.person_context as person_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_person_add_registers_household_member(monkeypatch, tmp_path: Path) -> None:
    original_build_person_service = person_commands.bootstrap.build_person_service

    def build_person_service_for_test():
        return original_build_person_service(data_dir=tmp_path)

    monkeypatch.setattr(
        person_commands.bootstrap,
        "build_person_service",
        build_person_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "person",
            "add",
            "--name",
            "Sara",
            "--household-member",
        ],
    )

    assert result.exit_code == 0
    assert "Person registered." in result.stdout
    assert "Sara" in result.stdout

    service = original_build_person_service(data_dir=tmp_path)
    people = service.list_recent(limit=10)

    assert len(people) == 1
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True


def test_person_add_rejects_empty_name() -> None:
    result = runner.invoke(
        cli.app,
        [
            "person",
            "add",
            "--name",
            "   ",
        ],
    )

    assert result.exit_code == 1
    assert "Person name cannot be empty." in result.stdout


def test_person_list_displays_people_and_household_status(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_person_service = person_commands.bootstrap.build_person_service

    def build_person_service_for_test():
        return original_build_person_service(data_dir=tmp_path)

    monkeypatch.setattr(
        person_commands.bootstrap,
        "build_person_service",
        build_person_service_for_test,
    )

    service = original_build_person_service(data_dir=tmp_path)
    service.register(name="HH", is_household_member=True)
    service.register(name="Guest", is_household_member=False)

    result = runner.invoke(
        cli.app,
        [
            "person",
            "list",
        ],
    )

    assert result.exit_code == 0
    assert "HH" in result.stdout
    assert "Guest" in result.stdout
    assert "household member" in result.stdout
    assert "known person" in result.stdout


def test_person_list_shows_no_people_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_person_service = person_commands.bootstrap.build_person_service

    def build_person_service_for_test():
        return original_build_person_service(data_dir=tmp_path)

    monkeypatch.setattr(
        person_commands.bootstrap,
        "build_person_service",
        build_person_service_for_test,
    )

    result = runner.invoke(cli.app, ["person", "list"])

    assert result.exit_code == 0
    assert "No people found." in result.stdout