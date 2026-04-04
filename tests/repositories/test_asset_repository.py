from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import AssetRepository


def test_asset_repository_create_saves_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        asset = repository.create(
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
        assert asset.retired_at is None
        assert asset.name == "Bosch Oven"
        assert asset.category == "Appliance"
        assert asset.location == "Kitchen"
        assert asset.brand == "Bosch"
        assert asset.model == "HBG6764S1"
        assert asset.serial_number == "SN-12345"
        assert asset.details == "Main built-in oven."
    finally:
        session_factory.close()


def test_asset_repository_get_by_id_returns_asset(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        created = repository.create(
            name="Bosch Oven",
            category="Appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven.",
        )

        loaded = repository.get_by_id(created.id)

        assert loaded is not None
        assert loaded.id == created.id
        assert loaded.name == "Bosch Oven"
    finally:
        session_factory.close()


def test_asset_repository_get_by_id_returns_none_when_missing(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        loaded = repository.get_by_id(999)

        assert loaded is None
    finally:
        session_factory.close()


def test_asset_repository_list_recent_returns_active_assets_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        repository.create(
            name="First asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Second asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )

        assets = repository.list_recent(limit=10)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Second asset",
            "First asset",
        ]
    finally:
        session_factory.close()


def test_asset_repository_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        repository.create(
            name="First asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Second asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Third asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )

        assets = repository.list_recent(limit=2)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Third asset",
            "Second asset",
        ]
    finally:
        session_factory.close()


def test_asset_repository_list_recent_excludes_retired_assets(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        active = repository.create(
            name="Active asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        retired = repository.create(
            name="Retired asset",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )

        with session_factory.get_session() as session:
            stored_retired = session.get(type(retired), retired.id)
            stored_retired.retired_at = stored_retired.created_at
            session.commit()

        assets = repository.list_recent(limit=10)

        assert [asset.name for asset in assets] == [active.name]
    finally:
        session_factory.close()


def test_asset_repository_search_returns_matching_active_assets_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        repository.create(
            name="Bosch Oven",
            category="Appliance",
            location="Kitchen",
            brand="Bosch",
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Dyson Vacuum",
            category="Cleaning",
            location="Utility room",
            brand="Dyson",
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Kitchen Mixer",
            category="Appliance",
            location="Pantry",
            brand="Kenwood",
            model=None,
            serial_number=None,
            details=None,
        )

        assets = repository.search(query="Kitchen", limit=10)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Kitchen Mixer",
            "Bosch Oven",
        ]
    finally:
        session_factory.close()


def test_asset_repository_search_matches_multiple_fields(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        repository.create(
            name="Bosch Oven",
            category="Appliance",
            location="Kitchen",
            brand="Bosch",
            model="HBG6764S1",
            serial_number="SN-12345",
            details="Main built-in oven",
        )
        repository.create(
            name="Dyson Vacuum",
            category="Cleaning",
            location="Utility room",
            brand="Dyson",
            model="V15 Detect",
            serial_number="SN-67890",
            details="Cordless vacuum cleaner",
        )

        by_brand = repository.search(query="Bosch", limit=10)
        by_model = repository.search(query="V15", limit=10)
        by_serial = repository.search(query="12345", limit=10)
        by_details = repository.search(query="cordless", limit=10)

        assert [asset.name for asset in by_brand] == ["Bosch Oven"]
        assert [asset.name for asset in by_model] == ["Dyson Vacuum"]
        assert [asset.name for asset in by_serial] == ["Bosch Oven"]
        assert [asset.name for asset in by_details] == ["Dyson Vacuum"]
    finally:
        session_factory.close()


def test_asset_repository_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        repository.create(
            name="Kitchen Lamp",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Kitchen Shelf",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        repository.create(
            name="Kitchen Stool",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )

        assets = repository.search(query="Kitchen", limit=2)

        assert len(assets) == 2
        assert [asset.name for asset in assets] == [
            "Kitchen Stool",
            "Kitchen Shelf",
        ]
    finally:
        session_factory.close()


def test_asset_repository_search_excludes_retired_assets(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = AssetRepository(session_factory)

    try:
        active = repository.create(
            name="Kitchen Lamp",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )
        retired = repository.create(
            name="Kitchen Shelf",
            category=None,
            location=None,
            brand=None,
            model=None,
            serial_number=None,
            details=None,
        )

        with session_factory.get_session() as session:
            stored_retired = session.get(type(retired), retired.id)
            stored_retired.retired_at = stored_retired.created_at
            session.commit()

        assets = repository.search(query="Kitchen", limit=10)

        assert [asset.name for asset in assets] == [active.name]
    finally:
        session_factory.close()