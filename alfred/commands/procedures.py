import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import Procedure


procedure_app = typer.Typer(help="Record and review procedures.")


def display_procedures(procedures: list[Procedure]) -> None:
    for procedure_record in procedures:
        pretty_timestamp = format_timestamp(procedure_record.created_at.isoformat())
        typer.echo(f"[{procedure_record.id}] {pretty_timestamp}")
        typer.echo(f"  Subject: {procedure_record.subject}")
        typer.echo(f"  Procedure: {procedure_record.procedure}")

        if procedure_record.category:
            typer.echo(f"  Category: {procedure_record.category}")

        if procedure_record.details:
            typer.echo(f"  Details: {procedure_record.details}")

        typer.echo()


@procedure_app.command("add")
def add(
    subject: str = typer.Option(..., "--subject", help="What the procedure is about."),
    procedure: str = typer.Option(..., "--procedure", help="The procedure itself."),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional category for the procedure.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional extra context for the procedure.",
    ),
) -> None:
    service = bootstrap.build_procedure_service()

    try:
        procedure_record = service.record(
            subject=subject,
            procedure=procedure,
            category=category,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Procedure recorded.")
    typer.echo(f"[{procedure_record.id}] {procedure_record.subject}")


@procedure_app.command("update")
def update(
    procedure_id: int = typer.Argument(
        ...,
        help="The ID of the procedure to update.",
    ),
    procedure: str = typer.Option(..., "--procedure", help="The updated procedure."),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional updated category for the procedure.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional updated extra context for the procedure.",
    ),
) -> None:
    service = bootstrap.build_procedure_service()

    try:
        procedure_record = service.update(
            procedure_id=procedure_id,
            procedure=procedure,
            category=category,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Procedure updated.")
    typer.echo(f"[{procedure_record.id}] {procedure_record.subject}")


@procedure_app.command("retire")
def retire(
    procedure_id: int = typer.Argument(
        ...,
        help="The ID of the procedure to retire.",
    ),
    reason: str | None = typer.Option(
        None,
        "--reason",
        help="Optional reason the procedure is no longer active.",
    ),
) -> None:
    service = bootstrap.build_procedure_service()

    try:
        procedure_record = service.retire(
            procedure_id=procedure_id,
            reason=reason,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Procedure retired.")
    typer.echo(f"[{procedure_record.id}] {procedure_record.subject}")


@procedure_app.command("list")
def list_procedures(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent procedures to show.",
    ),
) -> None:
    service = bootstrap.build_procedure_service()
    procedures: list[Procedure] = service.list_recent(limit=limit)

    if not procedures:
        typer.echo("No procedures found.")
        return

    display_procedures(procedures)