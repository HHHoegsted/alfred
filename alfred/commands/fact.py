import typer

import alfred.cli as cli
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
    cleaned_subject = subject.strip()
    cleaned_value = value.strip()
    cleaned_details = details.strip() if details is not None else None

    if not cleaned_subject:
        typer.echo("Subject cannot be empty.")
        raise typer.Exit(code=1)

    if not cleaned_value:
        typer.echo("Value cannot be empty.")
        raise typer.Exit(code=1)

    if cleaned_details == "":
        cleaned_details = None

    service = cli.build_household_fact_service()
    service.record(
        subject=cleaned_subject,
        value=cleaned_value,
        details=cleaned_details,
    )
    typer.echo("Household fact recorded.")


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
    service = cli.build_household_fact_service()
    facts: list[HouseholdFact] = service.list_recent(limit=limit)

    if not facts:
        typer.echo("No household facts found.")
        return

    display_facts(facts)