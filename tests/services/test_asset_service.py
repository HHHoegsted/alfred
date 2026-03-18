from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories.asset_repository import AssetRepository
from alfred.services.asset_service import AssetService


def test_asset_service_record_creates_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        service = AssetService(repository)

        asset = service.record(
            name="Bosch Oven",
            category="appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven.",
        )

    assert asset.id is not None
    assert asset.name == "Bosch Oven"
    assert asset.category == "appliance"
    assert asset.location == "Kitchen"
    assert asset.brand == "Bosch"
    assert asset.model == "HBG6764S1"
    assert asset.serial_number == "SN-12345"
    assert asset.details == "Main built-in oven."
    assert asset.created_at is not None
    assert asset.updated_at is None
    assert asset.retired_at is None
    assert asset.retired_reason is None


def test_asset_service_record_strips_fields_and_converts_blanks_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        service = AssetService(repository)

        asset = service.record(
            name="  Bosch Oven  ",
            category="  appliance  ",
            location="   ",
            brand="  Bosch  ",
            model="  HBG6764S1  ",
            serial_number="   ",
            details="   Main built-in oven.   ",
        )

    assert asset.name == "Bosch Oven"
    assert asset.category == "appliance"
    assert asset.location is None
    assert asset.brand == "Bosch"
    assert asset.model == "HBG6764S1"
    assert asset.serial_number is None
    assert asset.details == "Main built-in oven."


def test_asset_service_record_raises_for_empty_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        service = AssetService(repository)

        with pytest.raises(ValueError, match="Name cannot be empty."):
            service.record(
                name="   ",
                category="appliance",
                location="Kitchen",
                brand="Bosch",
                model="HBG6764S1",
                serial_number="SN-12345",
                details="Main built-in oven.",
            )


def test_asset_service_list_recent_returns_assets(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        service = AssetService(repository)

        older_asset = service.record(name="Living Room Rug")
        older_asset_id = older_asset.id

        newer_asset = service.record(name="Bosch Oven")
        newer_asset_id = newer_asset.id

        assets = service.list_recent()

    assert len(assets) == 2
    assert assets[0].id == newer_asset_id
    assert assets[1].id == older_asset_id