import typer
from datetime import datetime

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import Purchase


purchase_app = typer.Typer(help="Record and review purchases.")


def display_purchases(purchases: list[Purchase]) -> None:
    for purchase in purchases:
        pretty_timestamp = format_timestamp(purchase.created_at.isoformat())
        typer.echo(f"[{purchase.id}] {pretty_timestamp}")
        typer.echo(f"  Item: {purchase.item_name}")

        if purchase.vendor is not None:
            typer.echo(f"  Vendor: {purchase.vendor}")

        if purchase.purchase_date is not None:
            typer.echo(
                f"  Purchase date: {format_timestamp(purchase.purchase_date.isoformat())}"
            )

        if purchase.price_amount is not None:
            if purchase.currency is not None:
                typer.echo(f"  Price: {purchase.price_amount} {purchase.currency}")
            else:
                typer.echo(f"  Price: {purchase.price_amount}")

        if purchase.order_reference is not None:
            typer.echo(f"  Order reference: {purchase.order_reference}")

        if purchase.details is not None:
            typer.echo(f"  Details: {purchase.details}")

        typer.echo()


@purchase_app.command("record")
def record_purchase(
    item_name: str = typer.Argument(..., help="The purchased item name."),
    vendor: str | None = typer.Option(None, "--vendor", help="Where the item was bought."),
    purchase_date: str | None = typer.Option(
        None,
        "--purchase-date",
        help="Purchase date/time in ISO format, for example 2026-03-18T12:00:00.",
    ),
    price_amount: str | None = typer.Option(
        None,
        "--price-amount",
        help="The purchase amount as entered.",
    ),
    currency: str | None = typer.Option(
        None,
        "--currency",
        help="The purchase currency, for example DKK.",
    ),
    order_reference: str | None = typer.Option(
        None,
        "--order-reference",
        help="Order number or receipt reference.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Additional purchase details.",
    ),
) -> None:
    parsed_purchase_date: datetime | None = None

    if purchase_date is not None:
        cleaned_purchase_date = purchase_date.strip()

        if not cleaned_purchase_date:
            typer.echo("Purchase date cannot be empty.")
            raise typer.Exit(code=1)

        try:
            parsed_purchase_date = datetime.fromisoformat(cleaned_purchase_date)
        except ValueError as exc:
            typer.echo(
                "Purchase date must be a valid ISO datetime, for example 2026-03-18T12:00:00."
            )
            raise typer.Exit(code=1) from exc

    service = bootstrap.build_purchase_service()

    try:
        purchase = service.record(
            item_name=item_name,
            vendor=vendor,
            purchase_date=parsed_purchase_date,
            price_amount=price_amount,
            currency=currency,
            order_reference=order_reference,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo(f"Recorded purchase {purchase.id}: {purchase.item_name}")


@purchase_app.command("list")
def list_purchases(
    limit: int = typer.Option(
        20,
        "--limit",
        min=1,
        help="Maximum number of purchases to show.",
    ),
) -> None:
    service = bootstrap.build_purchase_service()
    purchases = service.list_recent(limit=limit)

    if not purchases:
        typer.echo("No purchases found.")
        return

    display_purchases(purchases)