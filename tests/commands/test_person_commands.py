from pathlib import Path

import alfred.commands.person_context as person_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_person_add_registers_household_member(
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
    assert "[1] Sara" in result.stdout

    service = original_build_person_service(data_dir=tmp_path)
    try:
        people = service.list_recent(limit=10)

        assert len(people) == 1
        assert people[0].name == "Sara"
        assert people[0].is_household_member is True
    finally:
        service.repository.session_factory.close()


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
    try:
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
    finally:
        service.repository.session_factory.close()


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


def test_person_list_accepts_short_limit_alias(
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
    try:
        service.register(name="First", is_household_member=False)
        service.register(name="Second", is_household_member=True)

        result = runner.invoke(cli.app, ["person", "list", "-n", "1"])

        assert result.exit_code == 0
        assert "Second" in result.stdout
        assert "First" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_person_search_returns_matching_people(
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
    try:
        service.register(name="Hans-Henrik", is_household_member=True)
        service.register(name="Sara", is_household_member=True)
        service.register(name="Hanne", is_household_member=False)

        result = runner.invoke(cli.app, ["person", "search", "han"])

        assert result.exit_code == 0
        assert "Hans-Henrik" in result.stdout
        assert "Hanne" in result.stdout
        assert "Sara" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_person_search_shows_no_people_message_when_no_matches(
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
    try:
        service.register(name="Sara", is_household_member=True)

        result = runner.invoke(cli.app, ["person", "search", "milk"])

        assert result.exit_code == 0
        assert "No people found." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_person_search_rejects_empty_query() -> None:
    result = runner.invoke(cli.app, ["person", "search", " "])

    assert result.exit_code == 1
    assert "Search query cannot be empty." in result.stdout


def test_person_search_accepts_short_limit_alias(
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
    try:
        service.register(name="Hans First", is_household_member=False)
        service.register(name="Hans Second", is_household_member=True)

        result = runner.invoke(cli.app, ["person", "search", "Hans", "-n", "1"])

        assert result.exit_code == 0
        assert "Hans Second" in result.stdout
        assert "Hans First" not in result.stdout
    finally:
        service.repository.session_factory.close()