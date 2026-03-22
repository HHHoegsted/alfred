import importlib
import sys
from pathlib import Path

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
    original_main = sys.modules.pop("__main__", None)
    original_cli_module = sys.modules.pop("alfred.cli", None)

    def fake_call(self, *args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(typer.Typer, "__call__", fake_call)

    try:
        importlib.import_module("alfred.cli")
        imported_module = sys.modules.pop("alfred.cli")
        imported_module.__name__ = "__main__"
        sys.modules["__main__"] = imported_module

        module_path = Path(imported_module.__file__)
        module_code = module_path.read_text(encoding="utf-8")
        exec(
            compile(module_code, str(module_path), "exec"),
            imported_module.__dict__,
        )
    finally:
        monkeypatch.setattr(typer.Typer, "__call__", original_call)

        sys.modules.pop("__main__", None)
        if original_main is not None:
            sys.modules["__main__"] = original_main

        sys.modules.pop("alfred.cli", None)
        if original_cli_module is not None:
            sys.modules["alfred.cli"] = original_cli_module

    assert called is True