from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories.asset_repository import AssetRepository


def test_asset_repository_create_persists_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)

        asset = repository.create(
            name="Bosch Oven",
            category="appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven.",
        )
        asset_id = asset.id

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        stored_asset = repository.get_by_id(asset_id)

    assert stored_asset is not None
    assert stored_asset.name == "Bosch Oven"
    assert stored_asset.category == "appliance"
    assert stored_asset.location == "Kitchen"
    assert stored_asset.brand == "Bosch"
    assert stored_asset.model == "HBG6764S1"
    assert stored_asset.serial_number == "SN-12345"
    assert stored_asset.details == "Main built-in oven."
    assert stored_asset.id is not None
    assert stored_asset.created_at is not None
    assert stored_asset.updated_at is None
    assert stored_asset.retired_at is None
    assert stored_asset.retired_reason is None


def test_asset_repository_get_by_id_returns_none_when_missing(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        asset = repository.get_by_id(9999)

    assert asset is None


def test_asset_repository_list_recent_returns_non_retired_assets_in_reverse_chronological_order(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)

        older_asset = repository.create(
            name="Living Room Rug",
            category="decor",
            location="Living Room",
            brand=None,
            model=None,
            serial_number=None,
            details="Large wool rug.",
        )
        older_asset_id = older_asset.id

        newer_asset = repository.create(
            name="Bosch Oven",
            category="appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven.",
        )
        newer_asset_id = newer_asset.id

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        assets = repository.list_recent()

    assert len(assets) == 2
    assert assets[0].id == newer_asset_id
    assert assets[1].id == older_asset_id


def test_asset_repository_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = AssetRepository(session)

        repository.create(
            name="Living Room Rug",
            category="decor",
            location="Living Room",
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        newest_asset = repository.create(
            name="Bosch Oven",
            category="appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details=None,
        )
        newest_asset_id = newest_asset.id

    with session_factory.get_session() as session:
        repository = AssetRepository(session)
        assets = repository.list_recent(limit=1)

    assert len(assets) == 1
    assert assets[0].id == newest_asset_id