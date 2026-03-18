from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_hello_prints_alive_message() -> None:
    result = runner.invoke(cli.app, ["hello"])

    assert result.exit_code == 0
    assert "Alfred is alive." in result.stdout