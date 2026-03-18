from pathlib import Path

from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_person_add_registers_household_member(monkeypatch, tmp_path: Path) -> None:
    original_build_person_service = cli.build_person_service

    def build_person_service_for_test():
        return original_build_person_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
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

    service = cli.build_person_service()
    people = service.list_recent(limit=10)

    assert len(people) == 1
    assert people[0].name == "Sara"
    assert people[0].is_household_member is True


def test_person_list_displays_people_and_household_status(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_person_service = cli.build_person_service

    def build_person_service_for_test():
        return original_build_person_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
        "build_person_service",
        build_person_service_for_test,
    )

    service = cli.build_person_service()
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