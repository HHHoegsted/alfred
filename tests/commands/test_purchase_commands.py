from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

from alfred import cli
from alfred.bootstrap import build_purchase_service


runner = CliRunner()


def test_purchase_record_saves_purchase_and_prints_confirmation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Miele Vacuum Cleaner",
            "--vendor",
            "Power",
            "--purchase-date",
            "2026-03-18T12:00:00",
            "--price-amount",
            "3499.00",
            "--currency",
            "DKK",
            "--order-reference",
            "ORD-2026-0001",
            "--details",
            "Bought for the current home.",
        ],
    )

    assert result.exit_code == 0
    assert "Recorded purchase" in result.stdout
    assert "Miele Vacuum Cleaner" in result.stdout

    service = cli.build_purchase_service()
    purchases = service.list_recent(limit=10)

    assert len(purchases) == 1
    assert purchases[0].item_name == "Miele Vacuum Cleaner"
    assert purchases[0].vendor == "Power"
    assert purchases[0].purchase_date == datetime(2026, 3, 18, 12, 0)
    assert purchases[0].price_amount == "3499.00"
    assert purchases[0].currency == "DKK"
    assert purchases[0].order_reference == "ORD-2026-0001"
    assert purchases[0].details == "Bought for the current home."


def test_purchase_record_uses_current_datetime_when_purchase_date_not_passed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Replacement Vacuum Bags",
            "--vendor",
            "Elgiganten",
        ],
    )

    assert result.exit_code == 0
    assert "Recorded purchase" in result.stdout
    assert "Replacement Vacuum Bags" in result.stdout

    service = cli.build_purchase_service()
    purchases = service.list_recent(limit=10)

    assert len(purchases) == 1
    assert purchases[0].item_name == "Replacement Vacuum Bags"
    assert purchases[0].vendor == "Elgiganten"
    assert purchases[0].purchase_date is not None


def test_purchase_record_rejects_empty_item_name(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "   ",
        ],
    )

    assert result.exit_code == 1
    assert "Item name cannot be empty." in result.stdout


def test_purchase_record_rejects_invalid_purchase_date(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Miele Vacuum Cleaner",
            "--purchase-date",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert "Purchase date must be a valid ISO datetime" in result.stdout


def test_purchase_list_shows_purchases(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    service = cli.build_purchase_service()
    service.record(
        item_name="Replacement Vacuum Bags",
        vendor="Elgiganten",
        purchase_date=datetime(2026, 3, 17, 12, 0),
        price_amount="199.00",
        currency="DKK",
        order_reference="ORD-2026-0002",
        details="For the Miele vacuum cleaner.",
    )
    service.record(
        item_name="Miele Vacuum Cleaner",
        vendor="Power",
        purchase_date=datetime(2026, 3, 18, 12, 0),
        price_amount="3499.00",
        currency="DKK",
        order_reference="ORD-2026-0001",
        details="Bought for the current home.",
    )

    result = runner.invoke(cli.app, ["purchase", "list"])

    assert result.exit_code == 0
    assert "Miele Vacuum Cleaner" in result.stdout
    assert "Replacement Vacuum Bags" in result.stdout
    assert "Vendor: Power" in result.stdout
    assert "Vendor: Elgiganten" in result.stdout


def test_purchase_list_shows_no_purchases_message_when_empty(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    result = runner.invoke(cli.app, ["purchase", "list"])

    assert result.exit_code == 0
    assert "No purchases found." in result.stdout


def test_purchase_list_respects_limit(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli,
        "build_purchase_service",
        lambda: build_purchase_service(data_dir=tmp_path),
    )

    service = cli.build_purchase_service()
    service.record(
        item_name="Replacement Vacuum Bags",
        purchase_date=datetime(2026, 3, 17, 12, 0),
    )
    service.record(
        item_name="Miele Vacuum Cleaner",
        purchase_date=datetime(2026, 3, 18, 12, 0),
    )

    result = runner.invoke(cli.app, ["purchase", "list", "--limit", "1"])

    assert result.exit_code == 0
    assert "Miele Vacuum Cleaner" in result.stdout
    assert "Replacement Vacuum Bags" not in result.stdout