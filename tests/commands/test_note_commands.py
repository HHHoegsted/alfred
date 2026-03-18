from pathlib import Path

from typer.testing import CliRunner

from alfred import cli
from alfred.bootstrap import build_note_service


runner = CliRunner()


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