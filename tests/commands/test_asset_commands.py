from pathlib import Path

from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_asset_record_saves_asset_and_prints_confirmation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = cli.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
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

    service = cli.build_asset_service()
    assets = service.list_recent(limit=10)

    assert len(assets) == 1
    assert assets[0].name == "Bosch Oven"
    assert assets[0].category == "appliance"
    assert assets[0].location == "Kitchen"
    assert assets[0].brand == "Bosch"
    assert assets[0].model == "HBG6764S1"
    assert assets[0].serial_number == "SN-12345"
    assert assets[0].details == "Main built-in oven."


def test_asset_record_rejects_blank_name(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = cli.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
        "build_asset_service",
        build_asset_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "asset",
            "record",
            "   ",
            "--category",
            "appliance",
        ],
    )

    assert result.exit_code != 0
    assert "Name cannot be empty." in result.stdout


def test_asset_list_shows_recorded_assets(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = cli.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
        "build_asset_service",
        build_asset_service_for_test,
    )

    service = cli.build_asset_service()
    service.record(
        name="Bosch Oven",
        category="appliance",
        location="Kitchen",
        brand="Bosch",
        model="HBG6764S1",
        serial_number="SN-12345",
        details="Main built-in oven.",
    )

    result = runner.invoke(cli.app, ["asset", "list"])

    assert result.exit_code == 0
    assert "Bosch Oven" in result.stdout
    assert "Category: appliance" in result.stdout
    assert "Location: Kitchen" in result.stdout
    assert "Brand: Bosch" in result.stdout
    assert "Model: HBG6764S1" in result.stdout
    assert "Serial number: SN-12345" in result.stdout
    assert "Details: Main built-in oven." in result.stdout


def test_asset_list_shows_no_assets_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_asset_service = cli.build_asset_service

    def build_asset_service_for_test():
        return original_build_asset_service(data_dir=tmp_path)

    monkeypatch.setattr(
        cli,
        "build_asset_service",
        build_asset_service_for_test,
    )

    result = runner.invoke(cli.app, ["asset", "list"])

    assert result.exit_code == 0
    assert "No assets found." in result.stdout


def test_asset_list_rejects_limit_below_one() -> None:
    result = runner.invoke(cli.app, ["asset", "list", "--limit", "0"])

    assert result.exit_code != 0