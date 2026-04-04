from datetime import datetime
from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import PurchaseRepository


def test_purchase_repository_create_saves_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    purchase_date = datetime(2026, 3, 1, 10, 30)

    try:
        purchase = repository.create(
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


def test_purchase_repository_get_by_id_returns_purchase(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        created = repository.create(
            item_name="Bosch Oven",
            vendor="Power",
            purchase_date=datetime(2026, 3, 1, 10, 30),
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )

        loaded = repository.get_by_id(created.id)

        assert loaded is not None
        assert loaded.id == created.id
        assert loaded.item_name == "Bosch Oven"
    finally:
        session_factory.close()


def test_purchase_repository_get_by_id_returns_none_when_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        loaded = repository.get_by_id(999)

        assert loaded is None
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_returns_active_purchases_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="First purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Second purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        purchases = repository.list_recent(limit=10)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Second purchase",
            "First purchase",
        ]
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="First purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Second purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Third purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        purchases = repository.list_recent(limit=2)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Third purchase",
            "Second purchase",
        ]
    finally:
        session_factory.close()


def test_purchase_repository_list_recent_excludes_retired_purchases(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        active = repository.create(
            item_name="Active purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        retired = repository.create(
            item_name="Retired purchase",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        with session_factory.get_session() as session:
            stored_retired = session.get(type(retired), retired.id)
            stored_retired.retired_at = stored_retired.created_at
            session.commit()

        purchases = repository.list_recent(limit=10)

        assert [purchase.item_name for purchase in purchases] == [active.item_name]
    finally:
        session_factory.close()


def test_purchase_repository_search_returns_matching_active_purchases_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="Bosch Oven",
            vendor="Power",
            purchase_date=None,
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )
        repository.create(
            item_name="Moccamaster",
            vendor="Elgiganten",
            purchase_date=None,
            price_amount="1999.00",
            currency="DKK",
            order_reference="ORDER-456",
            details="Coffee machine.",
        )
        repository.create(
            item_name="Kitchen Towels",
            vendor="IKEA",
            purchase_date=None,
            price_amount="99.00",
            currency="DKK",
            order_reference="ORDER-789",
            details="Blue kitchen textiles.",
        )

        purchases = repository.search(query="Kitchen", limit=10)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Kitchen Towels",
            "Bosch Oven",
        ]
    finally:
        session_factory.close()


def test_purchase_repository_search_matches_multiple_fields(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="Bosch Oven",
            vendor="Power",
            purchase_date=None,
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )
        repository.create(
            item_name="Moccamaster",
            vendor="Elgiganten",
            purchase_date=None,
            price_amount="1999.00",
            currency="DKK",
            order_reference="ORDER-456",
            details="Coffee machine.",
        )

        by_vendor = repository.search(query="Power", limit=10)
        by_amount = repository.search(query="1999", limit=10)
        by_currency = repository.search(query="DKK", limit=10)
        by_reference = repository.search(query="ORDER-123", limit=10)
        by_details = repository.search(query="coffee", limit=10)

        assert [purchase.item_name for purchase in by_vendor] == ["Bosch Oven"]
        assert [purchase.item_name for purchase in by_amount] == ["Moccamaster"]
        assert len(by_currency) == 2
        assert [purchase.item_name for purchase in by_reference] == ["Bosch Oven"]
        assert [purchase.item_name for purchase in by_details] == ["Moccamaster"]
    finally:
        session_factory.close()


def test_purchase_repository_search_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        repository.create(
            item_name="Kitchen Lamp",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Kitchen Shelf",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        repository.create(
            item_name="Kitchen Stool",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        purchases = repository.search(query="Kitchen", limit=2)

        assert len(purchases) == 2
        assert [purchase.item_name for purchase in purchases] == [
            "Kitchen Stool",
            "Kitchen Shelf",
        ]
    finally:
        session_factory.close()


def test_purchase_repository_search_excludes_retired_purchases(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = PurchaseRepository(session_factory)

    try:
        active = repository.create(
            item_name="Kitchen Lamp",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )
        retired = repository.create(
            item_name="Kitchen Shelf",
            vendor=None,
            purchase_date=None,
            price_amount=None,
            currency=None,
            order_reference=None,
            details=None,
        )

        with session_factory.get_session() as session:
            stored_retired = session.get(type(retired), retired.id)
            stored_retired.retired_at = stored_retired.created_at
            session.commit()

        purchases = repository.search(query="Kitchen", limit=10)

        assert [purchase.item_name for purchase in purchases] == [active.item_name]
    finally:
        session_factory.close()