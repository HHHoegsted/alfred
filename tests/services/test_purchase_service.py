from datetime import UTC, datetime
from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PurchaseRepository
from alfred.services import PurchaseService


def test_purchase_service_record_saves_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    purchase_date = datetime(2026, 3, 1, 10, 30)

    try:
        purchase = service.record(
            item_name="Bosch Oven",
            vendor="Power",
            purchase_date=purchase_date,
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )

        assert purchase.id is not None
        assert purchase.created_at is not None
        assert purchase.retired_at is None
        assert purchase.item_name == "Bosch Oven"
        assert purchase.vendor == "Power"
        assert purchase.purchase_date == purchase_date
        assert purchase.price_amount == "7499.95"
        assert purchase.currency == "DKK"
        assert purchase.order_reference == "ORDER-123"
        assert purchase.details == "Kitchen oven purchase."
    finally:
        session_factory.close()


def test_purchase_service_record_rejects_empty_item_name(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        with pytest.raises(ValueError, match="Purchase item name cannot be empty."):
            service.record(item_name="   ")
    finally:
        session_factory.close()


def test_purchase_service_record_strips_inputs_and_normalizes_blanks(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    purchase_date = datetime(2026, 3, 1, 10, 30)

    try:
        purchase = service.record(
            item_name="  Bosch Oven  ",
            vendor="  Power  ",
            purchase_date=purchase_date,
            price_amount="  7499.95  ",
            currency="  DKK  ",
            order_reference="  ORDER-123  ",
            details="  Kitchen oven purchase.  ",
        )

        assert purchase.item_name == "Bosch Oven"
        assert purchase.vendor == "Power"
        assert purchase.purchase_date == purchase_date
        assert purchase.price_amount == "7499.95"
        assert purchase.currency == "DKK"
        assert purchase.order_reference == "ORDER-123"
        assert purchase.details == "Kitchen oven purchase."
    finally:
        session_factory.close()


def test_purchase_service_record_converts_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        purchase = service.record(
            item_name="Bosch Oven",
            vendor="   ",
            purchase_date=None,
            price_amount="   ",
            currency="   ",
            order_reference="   ",
            details="   ",
        )

        assert purchase.vendor is None
        assert purchase.purchase_date is not None
        assert purchase.price_amount is None
        assert purchase.currency is None
        assert purchase.order_reference is None
        assert purchase.details is None
    finally:
        session_factory.close()


def test_purchase_service_record_defaults_purchase_date_when_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    before = datetime.now(UTC).replace(tzinfo=None)

    try:
        purchase = service.record(item_name="Bosch Oven")
        after = datetime.now(UTC).replace(tzinfo=None)

        assert purchase.purchase_date is not None
        assert before <= purchase.purchase_date <= after
    finally:
        session_factory.close()


def test_purchase_service_list_recent_returns_newest_first(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(item_name="First purchase")
        service.record(item_name="Second purchase")

        purchases = service.list_recent(limit=10)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Second purchase",
            "First purchase",
        ]
    finally:
        session_factory.close()


def test_purchase_service_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(item_name="First purchase")
        service.record(item_name="Second purchase")
        service.record(item_name="Third purchase")

        purchases = service.list_recent(limit=2)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Third purchase",
            "Second purchase",
        ]
    finally:
        session_factory.close()


def test_purchase_service_search_returns_matching_purchases(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(
            item_name="Bosch Oven",
            vendor="Power",
            details="Kitchen oven purchase.",
        )
        service.record(
            item_name="Moccamaster",
            vendor="Elgiganten",
            details="Coffee machine.",
        )
        service.record(
            item_name="Kitchen Towels",
            vendor="IKEA",
            details="Blue kitchen textiles.",
        )

        purchases = service.search(query="Kitchen", limit=10)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Kitchen Towels",
            "Bosch Oven",
        ]
    finally:
        session_factory.close()


def test_purchase_service_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(item_name="Kitchen Lamp")
        service.record(item_name="Kitchen Shelf")
        service.record(item_name="Kitchen Stool")

        purchases = service.search(query="Kitchen", limit=2)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Kitchen Stool",
            "Kitchen Shelf",
        ]
    finally:
        session_factory.close()


def test_purchase_service_search_rejects_blank_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        with pytest.raises(ValueError, match="Search query cannot be empty."):
            service.search(query="   ", limit=10)
    finally:
        session_factory.close()


def test_purchase_service_search_strips_query(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)
    service = PurchaseService(repository)

    try:
        service.record(item_name="Kitchen Lamp")
        service.record(item_name="Desk Lamp")

        purchases = service.search(query="  Kitchen  ", limit=10)

        assert len(purchases) == 1
        assert purchases[0].item_name == "Kitchen Lamp"
    finally:
        session_factory.close()