from datetime import datetime
from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PurchaseRepository
from alfred.services import PurchaseService


def test_purchase_service_record_saves_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        purchase = service.record(
            item_name="Miele Vacuum Cleaner",
            vendor="Power",
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount="3499.00",
            currency="DKK",
            order_reference="ORD-2026-0001",
            details="Bought for the current home.",
        )

        assert purchase.id is not None
        assert purchase.item_name == "Miele Vacuum Cleaner"
        assert purchase.vendor == "Power"
        assert purchase.purchase_date == datetime(2026, 3, 18, 12, 0)
        assert purchase.price_amount == "3499.00"
        assert purchase.currency == "DKK"
        assert purchase.order_reference == "ORD-2026-0001"
        assert purchase.details == "Bought for the current home."

        saved_purchases = repository.list_recent(limit=10)
        assert len(saved_purchases) == 1
        assert saved_purchases[0].item_name == "Miele Vacuum Cleaner"
    finally:
        session_factory.close()


def test_purchase_service_record_defaults_purchase_date_when_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        purchase = service.record(
            item_name="Replacement Vacuum Bags",
            vendor="Elgiganten",
            price_amount="199.00",
            currency="DKK",
            order_reference="ORD-2026-0002",
            details="For the Miele vacuum cleaner.",
        )

        assert purchase.id is not None
        assert purchase.item_name == "Replacement Vacuum Bags"
        assert purchase.vendor == "Elgiganten"
        assert purchase.purchase_date is not None
        assert purchase.price_amount == "199.00"
        assert purchase.currency == "DKK"
        assert purchase.order_reference == "ORD-2026-0002"
        assert purchase.details == "For the Miele vacuum cleaner."
    finally:
        session_factory.close()


def test_purchase_service_record_rejects_empty_item_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        with pytest.raises(ValueError, match="Purchase item name cannot be empty."):
            service.record(
                item_name="   ",
                vendor="Power",
                purchase_date=datetime(2026, 3, 18, 12, 0),
                price_amount="3499.00",
                currency="DKK",
                order_reference="ORD-2026-0001",
                details="Bought for the current home.",
            )
    finally:
        session_factory.close()


def test_purchase_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        purchase = service.record(
            item_name="Miele Vacuum Cleaner",
            vendor="   ",
            purchase_date=datetime(2026, 3, 18, 12, 0),
            price_amount="   ",
            currency="   ",
            order_reference="   ",
            details="   ",
        )

        assert purchase.vendor is None
        assert purchase.price_amount is None
        assert purchase.currency is None
        assert purchase.order_reference is None
        assert purchase.details is None
    finally:
        session_factory.close()


def test_purchase_service_list_recent_returns_purchases_in_reverse_created_order(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(
            item_name="First purchase",
            purchase_date=datetime(2026, 3, 17, 12, 0),
        )
        service.record(
            item_name="Second purchase",
            purchase_date=datetime(2026, 3, 18, 12, 0),
        )

        purchases = service.list_recent(limit=10)

        assert len(purchases) == 2
        assert purchases[0].item_name == "Second purchase"
        assert purchases[1].item_name == "First purchase"
    finally:
        session_factory.close()