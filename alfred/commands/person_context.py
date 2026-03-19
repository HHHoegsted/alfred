import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp


person_app = typer.Typer(help="Record and review known people.")


def display_people(people: list) -> None:
    if not people:
        typer.echo("No people found.")
        return

    for person in people:
        pretty_timestamp = format_timestamp(person.created_at.isoformat())
        membership = "household member" if person.is_household_member else "known person"
        typer.echo(f"[{person.id}] {pretty_timestamp}")
        typer.echo(f"  Name:   {person.name}")
        typer.echo(f"  Status: {membership}")
        typer.echo()


@person_app.command("add")
def add_person(
    name: str = typer.Option(
        ...,
        "--name",
        help="Name of the person to register.",
    ),
    household_member: bool = typer.Option(
        False,
        "--household-member",
        help="Mark this person as part of the current household.",
    ),
) -> None:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise typer.BadParameter("Person name cannot be empty.")

    service = bootstrap.build_person_service()
    person = service.register(
        name=cleaned_name,
        is_household_member=household_member,
    )
    typer.echo(f"Person registered. [#{person.id}] {person.name}")


@person_app.command("list")
def list_people(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent people to show.",
    ),
) -> None:
    service = bootstrap.build_person_service()
    people = service.list_recent(limit=limit)
    display_people(people)