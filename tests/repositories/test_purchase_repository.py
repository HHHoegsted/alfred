from datetime import datetime
from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import Purchase
from alfred.repositories import PurchaseRepository


def test_purchase_repository_create_and_list_recent(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        created = repository.create(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.item_name == "Miele Vacuum Cleaner"
        assert created.vendor == "Power"
        assert created.purchase_date == datetime(2026, 3, 18, 12, 0)
        assert created.price_amount == "3499.00"
        assert created.currency == "DKK"
        assert created.order_reference == "ORD-2026-0001"
        assert created.details == "Bought for the current home."

        purchases = repository.list_recent(limit=10)

        assert len(purchases) == 1
        assert purchases[0].id == created.id
        assert purchases[0].item_name == "Miele Vacuum Cleaner"
        assert purchases[0].vendor == "Power"
        assert purchases[0].purchase_date == datetime(2026, 3, 18, 12, 0)
        assert purchases[0].price_amount == "3499.00"
        assert purchases[0].currency == "DKK"
        assert purchases[0].order_reference == "ORD-2026-0001"
        assert purchases[0].details == "Bought for the current home."
    finally:
        session_factory.close()


def test_purchase_repository_get_by_id_returns_purchase(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        created = repository.create(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )

        purchase = repository.get_by_id(created.id)

        assert purchase is not None
        assert purchase.id == created.id
        assert purchase.item_name == "Miele Vacuum Cleaner"
        assert purchase.vendor == "Power"
    finally:
        session_factory.close()


def test_purchase_repository_get_by_id_returns_none_for_missing_purchase(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        purchase = repository.get_by_id(9999)

        assert purchase is None
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="First purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 17, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Second purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        purchases = repository.list_recent(limit=10)

        assert len(purchases) == 2
        assert purchases[0].item_name == "Second purchase"
        assert purchases[1].item_name == "First purchase"
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_excludes_retired_purchases(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        retired_purchase = repository.create(
            item_name="First purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 17, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Second purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        with session_factory.get_session() as session:
            purchase = session.get(Purchase, retired_purchase.id)
            assert purchase is not None
            purchase.retired_at = datetime(2026, 3, 19, 12, 0)
            session.add(purchase)
            session.commit()

        purchases = repository.list_recent(limit=10)

        assert len(purchases) == 1
        assert purchases[0].item_name == "Second purchase"
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="First purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 17, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Second purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Third purchase",
            vendor=None,
            purchase_date=datetime(2026, 3, 19, 12, 0),
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        purchases = repository.list_recent(limit=2)

        assert len(purchases) == 2
        assert purchases[0].item_name == "Third purchase"
        assert purchases[1].item_name == "Second purchase"
    finally:
        session_factory.close()