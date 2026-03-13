from pathlib import Path

from typer.testing import CliRunner

from alfred import cli

runner = CliRunner()


def test_hello_prints_alive_message() -> None:
    result = runner.invoke(cli.app, ["hello"])

    assert result.exit_code == 0
    assert "Alfred is alive" in result.stdout


def test_capture_saves_note_and_prints_confirmation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "get_data_dir", lambda: tmp_path)

    result = runner.invoke(cli.app, ["capture", "Remember the milk"])

    assert result.exit_code == 0
    assert "Note saved." in result.stdout

    list_result = runner.invoke(cli.app, ["list"])
    assert list_result.exit_code == 0
    assert "Remember the milk" in list_result.stdout


def test_capture_rejects_empty_note() -> None:
    result = runner.invoke(cli.app, ["capture", "   "])

    assert result.exit_code != 0
    assert "Note cannot be empty." in result.stderr


def test_list_shows_no_notes_message_when_database_is_empty(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "get_data_dir", lambda: tmp_path)

    result = runner.invoke(cli.app, ["list"])

    assert result.exit_code == 0
    assert "No notes found." in result.stdout


def test_list_rejects_limit_below_one() -> None:
    result = runner.invoke(cli.app, ["list", "--limit", "0"])

    assert result.exit_code != 0
    assert "0 is not in the range x>=1." in result.stderr


def test_search_returns_matching_notes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "get_data_dir", lambda: tmp_path)

    runner.invoke(cli.app, ["capture", "Buy Milk"])
    runner.invoke(cli.app, ["capture", "Walk the dog"])
    runner.invoke(cli.app, ["capture", "Remember milk for coffee"])

    result = runner.invoke(cli.app, ["search", "milk"])

    assert result.exit_code == 0
    assert "Buy Milk" in result.stdout
    assert "Remember milk for coffee" in result.stdout
    assert "Walk the dog" not in result.stdout


def test_search_shows_no_matches_message(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "get_data_dir", lambda: tmp_path)

    runner.invoke(cli.app, ["capture", "Walk the dog"])

    result = runner.invoke(cli.app, ["search", "milk"])

    assert result.exit_code == 0
    assert "No matching notes found." in result.stdout


def test_search_rejects_empty_query() -> None:
    result = runner.invoke(cli.app, ["search", "   "])

    assert result.exit_code != 0
    assert "Search query cannot be empty." in result.stderr


def test_search_rejects_limit_below_one() -> None:
    result = runner.invoke(cli.app, ["search", "milk", "--limit", "0"])

    assert result.exit_code != 0
    assert "0 is not in the range x>=1." in result.stderr
