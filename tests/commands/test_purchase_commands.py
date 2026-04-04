from pathlib import Path

import alfred.commands.purchase as purchase_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_purchase_record_saves_purchase_and_prints_confirmation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Bosch Oven",
            "--vendor",
            "Power",
            "--purchase-date",
            "2026-03-01T10:30:00",
            "--price-amount",
            "7499.95",
            "--currency",
            "DKK",
            "--order-reference",
            "ORDER-123",
            "--details",
            "Kitchen oven purchase.",
        ],
    )

    assert result.exit_code == 0
    assert "Purchase recorded." in result.stdout
    assert "[1] Bosch Oven" in result.stdout

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        purchases = service.list_recent(limit=10)

        assert len(purchases) == 1
        assert purchases[0].item_name == "Bosch Oven"
        assert purchases[0].vendor == "Power"
        assert purchases[0].price_amount == "7499.95"
        assert purchases[0].currency == "DKK"
        assert purchases[0].order_reference == "ORDER-123"
        assert purchases[0].details == "Kitchen oven purchase."
    finally:
        service.repository.session_factory.close()


def test_purchase_record_rejects_empty_item_name(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(cli.app, ["purchase", "record", "   "])

    assert result.exit_code == 1
    assert "Purchase item name cannot be empty." in result.stdout


def test_purchase_record_rejects_invalid_purchase_date(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Bosch Oven",
            "--purchase-date",
            "not-a-date",
        ],
    )

    assert result.exit_code == 1
    assert (
        "Purchase date must be a valid ISO datetime, for example "
        "2026-03-18T12:00:00."
    ) in result.stdout


def test_purchase_record_rejects_empty_purchase_date(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "purchase",
            "record",
            "Bosch Oven",
            "--purchase-date",
            "   ",
        ],
    )

    assert result.exit_code == 1
    assert "Purchase date cannot be empty." in result.stdout


def test_purchase_list_shows_recent_purchases(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(
            item_name="Bosch Oven",
            vendor="Power",
            purchase_date=None,
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )
        service.record(
            item_name="Moccamaster",
            vendor="Elgiganten",
            purchase_date=None,
            price_amount="1999.00",
            currency="DKK",
            order_reference="ORDER-456",
            details="Coffee machine.",
        )
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "list", "--limit", "1"])

    assert result.exit_code == 0
    assert "Moccamaster" in result.stdout
    assert "Bosch Oven" not in result.stdout


def test_purchase_list_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(item_name="Bosch Oven")
        service.record(item_name="Moccamaster")
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "list", "-n", "1"])

    assert result.exit_code == 0
    assert "Moccamaster" in result.stdout
    assert "Bosch Oven" not in result.stdout


def test_purchase_list_shows_no_purchases_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(cli.app, ["purchase", "list"])

    assert result.exit_code == 0
    assert "No purchases found." in result.stdout


def test_purchase_list_shows_price_without_currency(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(
            item_name="Desk Lamp",
            vendor="IKEA",
            purchase_date=None,
            price_amount="299.00",
            currency=None,
            order_reference=None,
            details=None,
        )
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "list"])

    assert result.exit_code == 0
    assert "Desk Lamp" in result.stdout
    assert "Price: 299.00" in result.stdout


def test_purchase_search_returns_matching_purchases(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(
            item_name="Bosch Oven",
            vendor="Power",
            price_amount="7499.95",
            currency="DKK",
            order_reference="ORDER-123",
            details="Kitchen oven purchase.",
        )
        service.record(
            item_name="Moccamaster",
            vendor="Elgiganten",
            price_amount="1999.00",
            currency="DKK",
            order_reference="ORDER-456",
            details="Coffee machine.",
        )
        service.record(
            item_name="Kitchen Towels",
            vendor="IKEA",
            price_amount="99.00",
            currency="DKK",
            order_reference="ORDER-789",
            details="Blue kitchen textiles.",
        )
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "search", "Kitchen"])

    assert result.exit_code == 0
    assert "Kitchen Towels" in result.stdout
    assert "Bosch Oven" in result.stdout
    assert "Moccamaster" not in result.stdout


def test_purchase_search_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(item_name="Kitchen Lamp")
        service.record(item_name="Kitchen Shelf")
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "search", "Kitchen", "-n", "1"])

    assert result.exit_code == 0
    assert "Kitchen Shelf" in result.stdout
    assert "Kitchen Lamp" not in result.stdout


def test_purchase_search_shows_no_purchases_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    service = original_build_purchase_service(data_dir=tmp_path)
    try:
        service.record(item_name="Bosch Oven")
    finally:
        service.repository.session_factory.close()

    result = runner.invoke(cli.app, ["purchase", "search", "Laundry"])

    assert result.exit_code == 0
    assert "No purchases found." in result.stdout


def test_purchase_search_rejects_blank_query(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_purchase_service = (
        purchase_commands.bootstrap.build_purchase_service
    )

    def build_purchase_service_for_test():
        return original_build_purchase_service(data_dir=tmp_path)

    monkeypatch.setattr(
        purchase_commands.bootstrap,
        "build_purchase_service",
        build_purchase_service_for_test,
    )

    result = runner.invoke(cli.app, ["purchase", "search", "   "])

    assert result.exit_code == 1
    assert "Search query cannot be empty." in result.stdout