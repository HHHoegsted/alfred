import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import HouseholdFact


fact_app = typer.Typer(help="Record and review household facts.")


def display_facts(facts: list[HouseholdFact]) -> None:
    for fact in facts:
        pretty_timestamp = format_timestamp(fact.created_at.isoformat())
        typer.echo(f"[{fact.id}] {pretty_timestamp}")
        typer.echo(f"  Subject: {fact.subject}")
        typer.echo(f"  Value: {fact.value}")
        if fact.details:
            typer.echo(f"  Details: {fact.details}")
        typer.echo()


@fact_app.command("add")
def add(
    subject: str = typer.Option(..., "--subject", help="What the fact is about."),
    value: str = typer.Option(..., "--value", help="The fact itself."),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional extra context for the fact.",
    ),
) -> None:
    service = bootstrap.build_household_fact_service()

    try:
        service.record(
            subject=subject,
            value=value,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Household fact recorded.")


@fact_app.command("update")
def update(
    fact_id: int = typer.Argument(..., help="The ID of the household fact to update."),
    value: str = typer.Option(..., "--value", help="The updated fact value."),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional updated extra context for the fact.",
    ),
) -> None:
    service = bootstrap.build_household_fact_service()

    try:
        service.update(
            fact_id=fact_id,
            value=value,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Household fact updated.")


@fact_app.command("retire")
def retire(
    fact_id: int = typer.Argument(..., help="The ID of the household fact to retire."),
    reason: str | None = typer.Option(
        None,
        "--reason",
        help="Optional reason the fact is no longer active.",
    ),
) -> None:
    service = bootstrap.build_household_fact_service()

    try:
        service.retire(
            fact_id=fact_id,
            reason=reason,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Household fact retired.")


@fact_app.command("list")
def list_facts(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent household facts to show.",
    ),
) -> None:
    service = bootstrap.build_household_fact_service()
    facts: list[HouseholdFact] = service.list_recent(limit=limit)

    if not facts:
        typer.echo("No household facts found.")
        return

    display_facts(facts)