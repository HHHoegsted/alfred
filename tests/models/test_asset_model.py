import sqlite3
from pathlib import Path

from alfred.bootstrap import init_sqlalchemy, get_db_path
from alfred.models import Asset


def test_asset_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

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
        assets = session.query(Asset).all()

    assert len(assets) == 1
    assert assets[0].name == "Bosch Oven"
    assert assets[0].category == "appliance"
    assert assets[0].location == "Kitchen"
    assert assets[0].brand == "Bosch"
    assert assets[0].model == "HBG6764S1"
    assert assets[0].serial_number == "SN-12345"
    assert assets[0].details == "Main built-in oven."
    assert assets[0].id is not None
    assert assets[0].created_at is not None
    assert assets[0].updated_at is None
    assert assets[0].retired_at is None
    assert assets[0].retired_reason is None

def test_init_sqlalchemy_creates_assets_table_with_expected_columns(
    tmp_path: Path,
) -> None:
    init_sqlalchemy(data_dir=tmp_path)

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