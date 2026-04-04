from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import AssetRepository
from alfred.services import AssetService


def test_asset_service_record_saves_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        asset = service.record(
            name="Bosch Oven",
            category="Appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven.",
        )

        assert asset.id is not None
        assert asset.created_at is not None
        assert asset.name == "Bosch Oven"
        assert asset.category == "Appliance"
        assert asset.location == "Kitchen"
        assert asset.brand == "Bosch"
        assert asset.model == "HBG6764S1"
        assert asset.serial_number == "SN-12345"
        assert asset.details == "Main built-in oven."

        assets = service.list_recent(limit=10)

        assert len(assets) == 1
        assert assets[0].name == "Bosch Oven"
        assert assets[0].category == "Appliance"
        assert assets[0].location == "Kitchen"
        assert assets[0].brand == "Bosch"
        assert assets[0].model == "HBG6764S1"
        assert assets[0].serial_number == "SN-12345"
        assert assets[0].details == "Main built-in oven."
    finally:
        session_factory.close()


def test_asset_service_record_rejects_empty_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        with pytest.raises(ValueError, match="Asset name cannot be empty."):
            service.record(
                name="   ",
                category="Appliance",
                location="Kitchen",
                brand="Bosch",
                model="HBG6764S1",
                serial_number="SN-12345",
                details="Main built-in oven.",
            )
    finally:
        session_factory.close()


def test_asset_service_record_strips_inputs(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        asset = service.record(
            name="  Bosch Oven  ",
            category="  Appliance  ",
            location="  Kitchen  ",
            brand="  Bosch  ",
            model="  HBG6764S1  ",
            serial_number="  SN-12345  ",
            details="  Main built-in oven.  ",
        )

        assert asset.name == "Bosch Oven"
        assert asset.category == "Appliance"
        assert asset.location == "Kitchen"
        assert asset.brand == "Bosch"
        assert asset.model == "HBG6764S1"
        assert asset.serial_number == "SN-12345"
        assert asset.details == "Main built-in oven."
    finally:
        session_factory.close()


def test_asset_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        asset = service.record(
            name="Bosch Oven",
            category="   ",
            location="   ",
            brand="   ",
            model="   ",
            serial_number="   ",
            details="   ",
        )

        assert asset.category is None
        assert asset.location is None
        assert asset.brand is None
        assert asset.model is None
        assert asset.serial_number is None
        assert asset.details is None
    finally:
        session_factory.close()


def test_asset_service_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        service.record(name="First asset")
        service.record(name="Second asset")

        assets = service.list_recent(limit=10)

        assert len(assets) == 2
        assert assets[0].name == "Second asset"
        assert assets[1].name == "First asset"
    finally:
        session_factory.close()


def test_asset_service_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        service.record(name="First asset")
        service.record(name="Second asset")
        service.record(name="Third asset")

        assets = service.list_recent(limit=2)

        assert len(assets) == 2
        assert assets[0].name == "Third asset"
        assert assets[1].name == "Second asset"
    finally:
        session_factory.close()


def test_asset_service_search_returns_matching_assets(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        service.record(
            name="Bosch Oven",
            category="Appliance",
            location="Kitchen",
            brand="Bosch",
        )
        service.record(
            name="Dyson Vacuum",
            category="Cleaning",
            location="Utility room",
            brand="Dyson",
        )
        service.record(
            name="Kitchen Mixer",
            category="Appliance",
            location="Pantry",
            brand="Kenwood",
        )

        assets = service.search(query="Kitchen", limit=10)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Kitchen Mixer",
            "Bosch Oven",
        ]
    finally:
        session_factory.close()


def test_asset_service_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        service.record(name="Kitchen Lamp")
        service.record(name="Kitchen Shelf")
        service.record(name="Kitchen Stool")

        assets = service.search(query="Kitchen", limit=2)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Kitchen Stool",
            "Kitchen Shelf",
        ]
    finally:
        session_factory.close()


def test_asset_service_search_rejects_blank_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        with pytest.raises(ValueError, match="Search query cannot be empty."):
            service.search(query="   ", limit=10)
    finally:
        session_factory.close()


def test_asset_service_search_strips_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)
    service = AssetService(repository)

    try:
        service.record(name="Kitchen Lamp")
        service.record(name="Desk Lamp")

        assets = service.search(query="  Kitchen  ", limit=10)

        assert len(assets) == 1
        assert assets[0].name == "Kitchen Lamp"
    finally:
        session_factory.close()