import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Asset


def test_asset_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            asset = Asset(
                name="Bosch Oven",
                category="appliance",
                location="Kitchen",
                brand="Bosch",
                model="HBG6764S1",
                serial_number="SN-12345",
                details="Main built-in oven.",
            )
            session.add(asset)
            session.commit()

        with session_factory.get_session() as session:
            stored_asset = session.query(Asset).one()

            asset_id = stored_asset.id
            name = stored_asset.name
            category = stored_asset.category
            location = stored_asset.location
            brand = stored_asset.brand
            model = stored_asset.model
            serial_number = stored_asset.serial_number
            details = stored_asset.details
            created_at = stored_asset.created_at
            updated_at = stored_asset.updated_at
            retired_at = stored_asset.retired_at
            retired_reason = stored_asset.retired_reason

        assert asset_id is not None
        assert name == "Bosch Oven"
        assert category == "appliance"
        assert location == "Kitchen"
        assert brand == "Bosch"
        assert model == "HBG6764S1"
        assert serial_number == "SN-12345"
        assert details == "Main built-in oven."
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_assets_table_with_expected_columns(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        db_path = get_db_path(tmp_path)
        connection = sqlite3.connect(db_path)
        try:
            table_cursor = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='assets'"
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute("PRAGMA table_info(assets)")
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "assets"
        assert "name" in columns
        assert "category" in columns
        assert "details" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()