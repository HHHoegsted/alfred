import runpy

import typer
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_hello_prints_alive_message() -> None:
    result = runner.invoke(cli.app, ["hello"])

    assert result.exit_code == 0
    assert "Alfred is alive." in result.stdout


def test_cli_module_calls_app_when_run_as_main(monkeypatch) -> None:
    called = False

    original_call = typer.Typer.__call__

    def fake_call(self, *args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(typer.Typer, "__call__", fake_call)

    try:
        runpy.run_module("alfred.cli", run_name="__main__")
    finally:
        monkeypatch.setattr(typer.Typer, "__call__", original_call)

    assert called is True