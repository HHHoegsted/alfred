from pathlib import Path

from typer.testing import CliRunner

from alfred import cli
from alfred.bootstrap import build_note_service


runner = CliRunner()


def test_hello_prints_alive_message() -> None:
    result = runner.invoke(cli.app, ["hello"])

    assert result.exit_code == 0
    assert "Alfred is alive." in result.stdout


def test_note_capture_saves_note_and_prints_confirmation(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        cli,
        "build_note_service",
        lambda: build_note_service(data_dir=tmp_path),
    )

    result = runner.invoke(cli.app, ["note", "capture", "Remember the milk"])

    assert result.exit_code == 0
    assert "Note captured." in result.stdout

    service = cli.build_note_service()
    notes = service.list_recent(limit=10)

    assert len(notes) == 1
    assert notes[0].text == "Remember the milk"


def test_note_capture_rejects_empty_note() -> None:
    result = runner.invoke(cli.app, ["note", "capture", " "])

    assert result.exit_code != 0
    assert "Note cannot be empty." in result.stdout


def test_note_list_shows_no_notes_message_when_database_is_empty(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        cli,
        "build_note_service",
        lambda: build_note_service(data_dir=tmp_path),
    )

    result = runner.invoke(cli.app, ["note", "list"])

    assert result.exit_code == 0
    assert "No notes found." in result.stdout


def test_note_list_rejects_limit_below_one() -> None:
    result = runner.invoke(cli.app, ["note", "list", "--limit", "0"])

    assert result.exit_code != 0


def test_note_search_returns_matching_notes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "build_note_service",
        lambda: build_note_service(data_dir=tmp_path),
    )

    runner.invoke(cli.app, ["note", "capture", "Buy Milk"])
    runner.invoke(cli.app, ["note", "capture", "Walk the dog"])
    runner.invoke(cli.app, ["note", "capture", "Remember milk for coffee"])

    result = runner.invoke(cli.app, ["note", "search", "milk"])

    assert result.exit_code == 0
    assert "Buy Milk" in result.stdout
    assert "Remember milk for coffee" in result.stdout
    assert "Walk the dog" not in result.stdout


def test_note_search_shows_no_matches_message(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "build_note_service",
        lambda: build_note_service(data_dir=tmp_path),
    )

    runner.invoke(cli.app, ["note", "capture", "Walk the dog"])
    result = runner.invoke(cli.app, ["note", "search", "milk"])

    assert result.exit_code == 0
    assert "No matching notes found." in result.stdout


def test_note_search_rejects_empty_query() -> None:
    result = runner.invoke(cli.app, ["note", "search", " "])

    assert result.exit_code != 0
    assert "Search query cannot be empty." in result.stdout


def test_note_search_rejects_limit_below_one() -> None:
    result = runner.invoke(cli.app, ["note", "search", "milk", "--limit", "0"])

    assert result.exit_code != 0


def test_person_add_registers_household_member(monkeypatch, tmp_path) -> None:
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
    tmp_path,
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

def test_fact_add_records_household_fact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = cli.build_household_fact_service

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
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

    service = cli.build_household_fact_service()
    facts = service.list_recent(limit=10)

    assert len(facts) == 1
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Under kitchen sink"
    assert facts[0].details == "Turn clockwise to close"


def test_fact_list_shows_recorded_household_facts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_household_fact_service = cli.build_household_fact_service

    def build_household_fact_service_for_test():
        return original_build_household_fact_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
        "build_household_fact_service",
        build_household_fact_service_for_test,
    )

    service = cli.build_household_fact_service()
    service.record(
        subject="Wi-Fi SSID",
        value="WorldHouseNet",
    )

    result = runner.invoke(cli.app, ["fact", "list"])

    assert result.exit_code == 0
    assert "Wi-Fi SSID" in result.stdout
    assert "WorldHouseNet" in result.stdout