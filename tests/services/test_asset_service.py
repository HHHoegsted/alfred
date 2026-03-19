from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import AssetRepository
from alfred.services import AssetService


def test_asset_service_record_saves_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    asset = service.record(
        name="LG Washing Machine",
        category="Appliance",
        location="Utility room",
        brand="LG",
        model="F4Y5EYP6J",
        serial_number="SN-12345",
        details="Bought for the current home.",
    )

    assert asset.id is not None
    assert asset.name == "LG Washing Machine"
    assert asset.category == "Appliance"
    assert asset.location == "Utility room"
    assert asset.brand == "LG"
    assert asset.model == "F4Y5EYP6J"
    assert asset.serial_number == "SN-12345"
    assert asset.details == "Bought for the current home."

    assets = service.list_recent(limit=10)
    assert len(assets) == 1
    assert assets[0].name == "LG Washing Machine"


def test_asset_service_record_rejects_empty_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    with pytest.raises(ValueError, match="Name cannot be empty."):
        service.record(
            name="   ",
            category="Appliance",
            location="Utility room",
            brand="LG",
            model="F4Y5EYP6J",
            serial_number="SN-12345",
            details="Bought for the current home.",
        )


def test_asset_service_record_strips_inputs(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    asset = service.record(
        name="  LG Washing Machine  ",
        category="  Appliance  ",
        location="  Utility room  ",
        brand="  LG  ",
        model="  F4Y5EYP6J  ",
        serial_number="  SN-12345  ",
        details="  Bought for the current home.  ",
    )

    assert asset.name == "LG Washing Machine"
    assert asset.category == "Appliance"
    assert asset.location == "Utility room"
    assert asset.brand == "LG"
    assert asset.model == "F4Y5EYP6J"
    assert asset.serial_number == "SN-12345"
    assert asset.details == "Bought for the current home."


def test_asset_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    asset = service.record(
        name="LG Washing Machine",
        category="   ",
        location="   ",
        brand="   ",
        model="   ",
        serial_number="   ",
        details="   ",
    )

    assert asset.name == "LG Washing Machine"
    assert asset.category is None
    assert asset.location is None
    assert asset.brand is None
    assert asset.model is None
    assert asset.serial_number is None
    assert asset.details is None


def test_asset_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    service.record(
        name="First asset",
        category=None,
        location=None,
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )
    service.record(
        name="Second asset",
        category=None,
        location=None,
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )

    assets = service.list_recent(limit=10)

    assert len(assets) == 2
    assert assets[0].name == "Second asset"
    assert assets[1].name == "First asset"


def test_asset_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    service.record(
        name="First asset",
        category=None,
        location=None,
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )
    service.record(
        name="Second asset",
        category=None,
        location=None,
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )
    service.record(
        name="Third asset",
        category=None,
        location=None,
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )

    assets = service.list_recent(limit=2)

    assert len(assets) == 2