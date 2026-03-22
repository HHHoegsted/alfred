from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_help_memory_prints_guidance() -> None:
    result = runner.invoke(cli.app, ["help-memory"])

    assert result.exit_code == 0
    assert "Alfred memory actions" in result.stdout
    assert "note capture" in result.stdout
    assert "decision record" in result.stdout
    assert "person add" in result.stdout
    assert "fact add" in result.stdout
    assert "asset record" in result.stdout
    assert "purchase record" in result.stdout