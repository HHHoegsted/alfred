import typer

import alfred.cli as cli
from alfred.models import Asset


asset_app = typer.Typer(help="Record and review household assets.")


def display_assets(assets: list[Asset]) -> None:
    for asset in assets:
        typer.echo(f"[{asset.id}] {asset.name}")

        if asset.category is not None:
            typer.echo(f"  Category: {asset.category}")

        if asset.location is not None:
            typer.echo(f"  Location: {asset.location}")

        if asset.brand is not None:
            typer.echo(f"  Brand: {asset.brand}")

        if asset.model is not None:
            typer.echo(f"  Model: {asset.model}")

        if asset.serial_number is not None:
            typer.echo(f"  Serial number: {asset.serial_number}")

        if asset.details is not None:
            typer.echo(f"  Details: {asset.details}")

        typer.echo()


@asset_app.command("record")
def record(
    name: str = typer.Argument(..., help="The asset name."),
    category: str | None = typer.Option(None, "--category", help="The asset category."),
    location: str | None = typer.Option(None, "--location", help="Where the asset is located."),
    brand: str | None = typer.Option(None, "--brand", help="The asset brand."),
    model: str | None = typer.Option(None, "--model", help="The asset model."),
    serial_number: str | None = typer.Option(
        None,
        "--serial-number",
        help="The asset serial number.",
    ),
    details: str | None = typer.Option(None, "--details", help="Additional asset details."),
) -> None:
    service = cli.build_asset_service()

    try:
        asset = service.record(
            name=name,
            category=category,
            location=location,
            brand=brand,
            model=model,
            serial_number=serial_number,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo(f"Recorded asset {asset.id}: {asset.name}")


@asset_app.command("list")
def list_recent(
    limit: int = typer.Option(20, "--limit", min=1, help="Maximum number of assets to show."),
) -> None:
    service = cli.build_asset_service()
    assets = service.list_recent(limit=limit)

    if not assets:
        typer.echo("No assets found.")
        return

    display_assets(assets)