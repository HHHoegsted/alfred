from pathlib import Path

from alfred.bootstrap import build_asset_service
from alfred.repositories import AssetRepository


def build_asset_repository(tmp_path: Path) -> AssetRepository:
    service = build_asset_service(data_dir=tmp_path)
    return service.repository


def test_create_stores_asset(tmp_path: Path) -> None:
    repository = build_asset_repository(tmp_path)

    asset = repository.create(
        name="Vacuum cleaner",
        category="Appliance",
        location="Utility room",
        brand="Miele",
        model="Complete C3",
        serial_number="VC-123",
        details="Main household vacuum",
    )

    assert asset.id is not None
    assert asset.name == "Vacuum cleaner"
    assert asset.category == "Appliance"
    assert asset.location == "Utility room"
    assert asset.brand == "Miele"
    assert asset.model == "Complete C3"
    assert asset.serial_number == "VC-123"
    assert asset.details == "Main household vacuum"


def test_get_by_id_returns_asset(tmp_path: Path) -> None:
    repository = build_asset_repository(tmp_path)
    created_asset = repository.create(
        name="Air fryer",
        category="Kitchen",
        location="Pantry",
        brand="Philips",
        model="XL",
        serial_number="AF-456",
        details="Bought for quick dinners",
    )

    asset = repository.get_by_id(created_asset.id)

    assert asset is not None
    assert asset.id == created_asset.id
    assert asset.name == "Air fryer"


def test_get_by_id_returns_none_for_missing_asset(tmp_path: Path) -> None:
    repository = build_asset_repository(tmp_path)

    asset = repository.get_by_id(999)

    assert asset is None


def test_list_recent_returns_non_retired_assets_newest_first(tmp_path: Path) -> None:
    repository = build_asset_repository(tmp_path)

    first_asset = repository.create(
        name="Old toaster",
        category="Kitchen",
        location="Cupboard",
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )
    second_asset = repository.create(
        name="New toaster",
        category="Kitchen",
        location="Counter",
        brand=None,
        model=None,
        serial_number=None,
        details=None,
    )

    first_asset.retired_at = first_asset.created_at
    repository.session_factory.get_session().__enter__  # keep linters from assuming unused? no, remove
    with repository.session_factory.get_session() as session:
        persisted_first_asset = session.get(type(first_asset), first_asset.id)
        assert persisted_first_asset is not None
        persisted_first_asset.retired_at = persisted_first_asset.created_at
        session.add(persisted_first_asset)
        session.commit()

    assets = repository.list_recent()

    assert [asset.id for asset in assets] == [second_asset.id]