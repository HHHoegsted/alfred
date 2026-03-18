from pathlib import Path

import alfred.commands.assets as asset_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_asset_record_saves_asset_and_prints_confirmation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = asset_commands.bootstrap.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        asset_commands.bootstrap,
        "build_asset_service",
        build_asset_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "asset",
            "record",
            "Bosch Oven",
            "--category",
            "appliance",
            "--location",
            "Kitchen",
            "--brand",
            "Bosch",
            "--model",
            "HBG6764S1",
            "--serial-number",
            "SN-12345",
            "--details",
            "Main built-in oven.",
        ],
    )

    assert result.exit_code == 0
    assert "Recorded asset" in result.stdout
    assert "Bosch Oven" in result.stdout

    service = original_build_asset_service(data_dir=tmp_path)
    assets = service.list_recent(limit=10)

    assert len(assets) == 1
    assert assets[0].name == "Bosch Oven"
    assert assets[0].category == "appliance"
    assert assets[0].location == "Kitchen"
    assert assets[0].brand == "Bosch"
    assert assets[0].model == "HBG6764S1"
    assert assets[0].serial_number == "SN-12345"
    assert assets[0].details == "Main built-in oven."


def test_asset_record_rejects_empty_name(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = asset_commands.bootstrap.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        asset_commands.bootstrap,
        "build_asset_service",
        build_asset_service_for_test,
    )

    result = runner.invoke(cli.app, ["asset", "record", "   "])

    assert result.exit_code == 1
    assert "Name cannot be empty." in result.stdout


def test_asset_list_shows_assets(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = asset_commands.bootstrap.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        asset_commands.bootstrap,
        "build_asset_service",
        build_asset_service_for_test,
    )

    service = original_build_asset_service(data_dir=tmp_path)
    service.record(
        name="Bosch Oven",
        category="appliance",
        location="Kitchen",
        brand="Bosch",
        model="HBG6764S1",
        serial_number="SN-12345",
        details="Main built-in oven.",
    )
    service.record(
        name="Dyson Vacuum",
        category="cleaning",
        location="Utility room",
        brand="Dyson",
        model="V15 Detect",
        serial_number="SN-67890",
        details="Cordless vacuum cleaner.",
    )

    result = runner.invoke(cli.app, ["asset", "list"])

    assert result.exit_code == 0
    assert "Bosch Oven" in result.stdout
    assert "Dyson Vacuum" in result.stdout
    assert "Kitchen" in result.stdout
    assert "Utility room" in result.stdout


def test_asset_list_shows_no_assets_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = asset_commands.bootstrap.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        asset_commands.bootstrap,
        "build_asset_service",
        build_asset_service_for_test,
    )

    result = runner.invoke(cli.app, ["asset", "list"])

    assert result.exit_code == 0
    assert "No assets found." in result.stdout


def test_asset_list_respects_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = asset_commands.bootstrap.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        asset_commands.bootstrap,
        "build_asset_service",
        build_asset_service_for_test,
    )

    service = original_build_asset_service(data_dir=tmp_path)
    service.record(name="Bosch Oven")
    service.record(name="Dyson Vacuum")

    result = runner.invoke(cli.app, ["asset", "list", "--limit", "1"])

    assert result.exit_code == 0
    assert "Dyson Vacuum" in result.stdout
    assert "Bosch Oven" not in result.stdout