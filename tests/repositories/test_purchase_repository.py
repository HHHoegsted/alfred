from datetime import datetime
from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PurchaseRepository


def test_purchase_repository_create_persists_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    purchase_date = datetime(2026, 3, 18, 12, 0)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)

        purchase = repository.create(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=purchase_date,
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )
        purchase_id = purchase.id

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        stored_purchase = repository.get_by_id(purchase_id)

    assert stored_purchase is not None
    assert stored_purchase.item_name == "Miele Vacuum Cleaner"
    assert stored_purchase.vendor == "Power"
    assert stored_purchase.purchase_date == purchase_date
    assert stored_purchase.price_amount == "3499.00"
    assert stored_purchase.currency == "DKK"
    assert stored_purchase.order_reference == "ORD-2026-0001"
    assert stored_purchase.details == "Bought for the current home."
    assert stored_purchase.id is not None
    assert stored_purchase.created_at is not None
    assert stored_purchase.updated_at is None
    assert stored_purchase.retired_at is None
    assert stored_purchase.retired_reason is None


def test_purchase_repository_get_by_id_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        purchase = repository.get_by_id(9999)

    assert purchase is None


def test_purchase_repository_list_recent_returns_non_retired_purchases_in_reverse_chronological_order(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    older_purchase_date = datetime(2026, 3, 17, 12, 0)
    newer_purchase_date = datetime(2026, 3, 18, 12, 0)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)

        older_purchase = repository.create(
            item_name="Replacement Vacuum Bags",
            vendor="Elgiganten",
            purchase_date=older_purchase_date,
            price_amount="199.00",
            currency="DKK",
            order_reference="ORD-2026-0002",
            details="For the Miele vacuum cleaner.",
        )
        older_purchase_id = older_purchase.id

        newer_purchase = repository.create(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=newer_purchase_date,
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )
        newer_purchase_id = newer_purchase.id

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        purchases = repository.list_recent()

    assert len(purchases) == 2
    assert purchases[0].id == newer_purchase_id
    assert purchases[1].id == older_purchase_id


def test_purchase_repository_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)

        repository.create(
            item_name="Replacement Vacuum Bags",
            vendor="Elgiganten",
            purchase_date=datetime(2026, 3, 17, 12, 0),
            price_amount="199.00",
            currency="DKK",
            order_reference="ORD-2026-0002",
            details=None,
        )
        newest_purchase = repository.create(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details=None,
        )
        newest_purchase_id = newest_purchase.id

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        purchases = repository.list_recent(limit=1)

    assert len(purchases) == 1
    assert purchases[0].id == newest_purchase_id