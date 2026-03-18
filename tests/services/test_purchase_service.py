from datetime import datetime
from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PurchaseRepository
from alfred.services import PurchaseService


def test_purchase_service_record_creates_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    purchase_date = datetime(2026, 3, 18, 12, 0)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)

        purchase = service.record(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=purchase_date,
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )

    assert purchase.id is not None
    assert purchase.item_name == "Miele Vacuum Cleaner"
    assert purchase.vendor == "Power"
    assert purchase.purchase_date == purchase_date
    assert purchase.price_amount == "3499.00"
    assert purchase.currency == "DKK"
    assert purchase.order_reference == "ORD-2026-0001"
    assert purchase.details == "Bought for the current home."
    assert purchase.created_at is not None
    assert purchase.updated_at is None
    assert purchase.retired_at is None
    assert purchase.retired_reason is None


def test_purchase_service_record_strips_fields_and_converts_blanks_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    purchase_date = datetime(2026, 3, 18, 12, 0)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)

        purchase = service.record(
            item_name="  Miele Vacuum Cleaner  ",
            vendor="  Power  ",
            purchase_date=purchase_date,
            price_amount="  3499.00  ",
            currency="  DKK  ",
            order_reference="   ",
            details="   Bought for the current home.   ",
        )

    assert purchase.item_name == "Miele Vacuum Cleaner"
    assert purchase.vendor == "Power"
    assert purchase.purchase_date == purchase_date
    assert purchase.price_amount == "3499.00"
    assert purchase.currency == "DKK"
    assert purchase.order_reference is None
    assert purchase.details == "Bought for the current home."


def test_purchase_service_record_sets_purchase_date_when_not_passed(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)

        before = datetime.now()
        purchase = service.record(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )
        after = datetime.now()

    assert purchase.purchase_date is not None
    assert before <= purchase.purchase_date <= after


def test_purchase_service_record_raises_for_empty_item_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)

        with pytest.raises(ValueError, match="Item name cannot be empty."):
            service.record(
                item_name="   ",
                vendor="Power",
                price_amount="3499.00",
                currency="DKK",
                order_reference="ORD-2026-0001",
                details="Bought for the current home.",
            )


def test_purchase_service_list_recent_returns_purchases(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)

        older_purchase = service.record(item_name="Replacement Vacuum Bags")
        older_purchase_id = older_purchase.id

        newer_purchase = service.record(item_name="Miele Vacuum Cleaner")
        newer_purchase_id = newer_purchase.id

    with session_factory.get_session() as session:
        repository = PurchaseRepository(session)
        service = PurchaseService(repository)
        purchases = service.list_recent()

    assert len(purchases) == 2
    assert purchases[0].id == newer_purchase_id
    assert purchases[1].id == older_purchase_id