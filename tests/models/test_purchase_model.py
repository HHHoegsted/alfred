import sqlite3
from pathlib import Path

from alfred.bootstrap import get_db_path, init_sqlalchemy
from alfred.models import Purchase


def test_purchase_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        with session_factory.get_session() as session:
            purchase = Purchase(
                item_name="Miele Vacuum Cleaner",
                vendor="Power",
                price_amount="3499.00",
                currency="DKK",
                order_reference="ORD-2026-0001",
                details="Bought for the current home.",
            )
            session.add(purchase)
            session.commit()

        with session_factory.get_session() as session:
            stored_purchase = session.query(Purchase).one()

            purchase_id = stored_purchase.id
            item_name = stored_purchase.item_name
            vendor = stored_purchase.vendor
            price_amount = stored_purchase.price_amount
            currency = stored_purchase.currency
            order_reference = stored_purchase.order_reference
            details = stored_purchase.details
            created_at = stored_purchase.created_at
            updated_at = stored_purchase.updated_at
            retired_at = stored_purchase.retired_at
            retired_reason = stored_purchase.retired_reason

        assert purchase_id is not None
        assert item_name == "Miele Vacuum Cleaner"
        assert vendor == "Power"
        assert price_amount == "3499.00"
        assert currency == "DKK"
        assert order_reference == "ORD-2026-0001"
        assert details == "Bought for the current home."
        assert created_at is not None
        assert updated_at is None
        assert retired_at is None
        assert retired_reason is None
    finally:
        session_factory.close()


def test_init_sqlalchemy_creates_purchases_table_with_expected_columns(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    try:
        db_path = get_db_path(tmp_path)
        connection = sqlite3.connect(db_path)
        try:
            table_cursor = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='purchases'"
            )
            table_row = table_cursor.fetchone()

            column_cursor = connection.execute("PRAGMA table_info(purchases)")
            columns = [row[1] for row in column_cursor.fetchall()]
        finally:
            connection.close()

        assert table_row is not None
        assert table_row[0] == "purchases"
        assert "item_name" in columns
        assert "vendor" in columns
        assert "purchase_date" in columns
        assert "price_amount" in columns
        assert "currency" in columns
        assert "order_reference" in columns
        assert "details" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "retired_at" in columns
        assert "retired_reason" in columns
    finally:
        session_factory.close()