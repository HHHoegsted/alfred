from datetime import datetime
from pathlib import Path

from alfred.bootstrap import build_purchase_service
from alfred.repositories import PurchaseRepository


def build_purchase_repository(tmp_path: Path) -> PurchaseRepository:
    service = build_purchase_service(data_dir=tmp_path)
    return service.repository


def test_create_stores_purchase(tmp_path: Path) -> None:
    repository = build_purchase_repository(tmp_path)

    purchase_date = datetime(2026, 3, 19, 12, 0, 0)
    purchase = repository.create(
        item_name="Robot vacuum",
        vendor="Power",
        purchase_date=purchase_date,
        price_amount="3999.95",
        currency="DKK",
        order_reference="ORDER-123",
        details="Upstairs cleaning helper",
    )

    assert purchase.id is not None
    assert purchase.item_name == "Robot vacuum"
    assert purchase.vendor == "Power"
    assert purchase.purchase_date == purchase_date
    assert purchase.price_amount == "3999.95"
    assert purchase.currency == "DKK"
    assert purchase.order_reference == "ORDER-123"
    assert purchase.details == "Upstairs cleaning helper"


def test_get_by_id_returns_purchase(tmp_path: Path) -> None:
    repository = build_purchase_repository(tmp_path)
    created_purchase = repository.create(
        item_name="Dishwasher tablets",
        vendor="Bilka",
        purchase_date=datetime(2026, 3, 1, 8, 30, 0),
        price_amount="129.00",
        currency="DKK",
        order_reference="BILKA-1",
        details="Bulk pack",
    )

    purchase = repository.get_by_id(created_purchase.id)

    assert purchase is not None
    assert purchase.id == created_purchase.id
    assert purchase.item_name == "Dishwasher tablets"


def test_get_by_id_returns_none_for_missing_purchase(tmp_path: Path) -> None:
    repository = build_purchase_repository(tmp_path)

    purchase = repository.get_by_id(999)

    assert purchase is None


def test_list_recent_returns_non_retired_purchases_newest_first(tmp_path: Path) -> None:
    repository = build_purchase_repository(tmp_path)

    first_purchase = repository.create(
        item_name="Old item",
        vendor="Shop A",
        purchase_date=datetime(2026, 1, 1, 10, 0, 0),
        price_amount="10.00",
        currency="DKK",
        order_reference=None,
        details=None,
    )
    second_purchase = repository.create(
        item_name="New item",
        vendor="Shop B",
        purchase_date=datetime(2026, 2, 1, 10, 0, 0),
        price_amount="20.00",
        currency="DKK",
        order_reference=None,
        details=None,
    )

    with repository.session_factory.get_session() as session:
        persisted_first_purchase = session.get(type(first_purchase), first_purchase.id)
        assert persisted_first_purchase is not None
        persisted_first_purchase.retired_at = persisted_first_purchase.created_at
        session.add(persisted_first_purchase)
        session.commit()

    purchases = repository.list_recent()

    assert [purchase.id for purchase in purchases] == [second_purchase.id]