from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
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