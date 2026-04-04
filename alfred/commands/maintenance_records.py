import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import MaintenanceRecord


maintenance_record_app = typer.Typer(help="Record and review maintenance records.")


def display_maintenance_records(
    maintenance_records: list[MaintenanceRecord],
) -> None:
    for maintenance_record in maintenance_records:
        pretty_created_timestamp = format_timestamp(
            maintenance_record.created_at.isoformat()
        )
        pretty_performed_timestamp = format_timestamp(
            maintenance_record.performed_at.isoformat()
        )

        typer.echo(f"[{maintenance_record.id}] {pretty_created_timestamp}")
        typer.echo(f"  Subject: {maintenance_record.subject}")
        typer.echo(f"  Performed: {pretty_performed_timestamp}")
        typer.echo(f"  Details: {maintenance_record.details}")

        if maintenance_record.category:
            typer.echo(f"  Category: {maintenance_record.category}")

        if maintenance_record.notes:
            typer.echo(f"  Notes: {maintenance_record.notes}")

        typer.echo()


@maintenance_record_app.command("add")
def add(
    subject: str = typer.Option(
        ...,
        "--subject",
        help="What the maintenance record is about.",
    ),
    performed_at: str = typer.Option(
        ...,
        "--performed-at",
        help="When the maintenance was performed, as an ISO 8601 datetime.",
    ),
    details: str = typer.Option(
        ...,
        "--details",
        help="What maintenance was performed.",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional category for the maintenance record.",
    ),
    notes: str | None = typer.Option(
        None,
        "--notes",
        help="Optional extra context for the maintenance record.",
    ),
) -> None:
    service = bootstrap.build_maintenance_record_service()

    try:
        maintenance_record = service.record(
            subject=subject,
            performed_at=performed_at,
            details=details,
            category=category,
            notes=notes,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Maintenance record recorded.")
    typer.echo(f"[{maintenance_record.id}] {maintenance_record.subject}")


@maintenance_record_app.command("update")
def update(
    maintenance_record_id: int = typer.Argument(
        ...,
        help="The ID of the maintenance record to update.",
    ),
    performed_at: str = typer.Option(
        ...,
        "--performed-at",
        help="The updated performed-at timestamp as an ISO 8601 datetime.",
    ),
    details: str = typer.Option(
        ...,
        "--details",
        help="The updated maintenance details.",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional updated category for the maintenance record.",
    ),
    notes: str | None = typer.Option(
        None,
        "--notes",
        help="Optional updated extra context for the maintenance record.",
    ),
) -> None:
    service = bootstrap.build_maintenance_record_service()

    try:
        maintenance_record = service.update(
            maintenance_record_id=maintenance_record_id,
            performed_at=performed_at,
            details=details,
            category=category,
            notes=notes,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Maintenance record updated.")
    typer.echo(f"[{maintenance_record.id}] {maintenance_record.subject}")


@maintenance_record_app.command("retire")
def retire(
    maintenance_record_id: int = typer.Argument(
        ...,
        help="The ID of the maintenance record to retire.",
    ),
    reason: str | None = typer.Option(
        None,
        "--reason",
        help="Optional reason the maintenance record is no longer active.",
    ),
) -> None:
    service = bootstrap.build_maintenance_record_service()

    try:
        maintenance_record = service.retire(
            maintenance_record_id=maintenance_record_id,
            reason=reason,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Maintenance record retired.")
    typer.echo(f"[{maintenance_record.id}] {maintenance_record.subject}")


@maintenance_record_app.command("list")
def list_maintenance_records(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent maintenance records to show.",
    ),
) -> None:
    service = bootstrap.build_maintenance_record_service()

    try:
        maintenance_records: list[MaintenanceRecord] = service.list_recent(limit=limit)
    finally:
        service.repository.session_factory.close()

    if not maintenance_records:
        typer.echo("No maintenance records found.")
        return

    display_maintenance_records(maintenance_records)