import sqlite3

import typer

from alfred.bootstrap import (
    build_decision_record_service,
    build_note_service,
    build_person_service,
)
from alfred.common import format_timestamp

### App and Sub-apps

app = typer.Typer(help="Alfred is a local-first CLI for capturing and reviewing household memory.")

decision_app = typer.Typer(help="Record and review structured decisions.")
app.add_typer(decision_app, name="decision")

person_app = typer.Typer(help="Record and review known people.")
app.add_typer(person_app, name="person")

### Display methods

def display_notes(notes: list[sqlite3.Row]) -> None:
    for note in notes:
        pretty_timestamp = format_timestamp(note["timestamp"])
        typer.echo(f"[{note['id']}] {pretty_timestamp}")
        typer.echo(f"  {note['text']}")
        typer.echo()


def display_decision_records(records: list) -> None:
    if not records:
        typer.echo("No decision records found.")
        return

    for record in records:
        pretty_timestamp = format_timestamp(record.created_at.isoformat())
        typer.echo(f"[{record.id}] {pretty_timestamp}")
        typer.echo(f"  Summary: {record.summary}")
        typer.echo(f"  Reason:  {record.reason}")
        typer.echo()


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

### Commands

@app.command()
def hello() -> None:
    typer.echo("Alfred is alive.")


@app.command()
def capture(
    text: str = typer.Argument(..., help="The note text to save."),
) -> None:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise typer.BadParameter("Note cannot be empty.")

    service = build_note_service()
    service.capture(cleaned_text)
    typer.echo("Note captured.")


@app.command("list")
def list_notes(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent notes to show.",
    ),
) -> None:
    service = build_note_service()
    notes: list[sqlite3.Row] = service.list_recent(limit=limit)

    if not notes:
        typer.echo("No notes found.")
        return

    display_notes(notes)


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Text to search for in saved notes."),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of matching notes to show.",
    ),
) -> None:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise typer.BadParameter("Search query cannot be empty.")

    service = build_note_service()
    notes: list[sqlite3.Row] = service.search(query=cleaned_query, limit=limit)

    if not notes:
        typer.echo("No matching notes found.")
        return

    display_notes(notes)


@decision_app.command("record")
def record_decision(
    summary: str = typer.Option(
        ...,
        "--summary",
        help="Short statement of what was decided.",
    ),
    reason: str = typer.Option(
        ...,
        "--reason",
        help="Why the decision was made.",
    ),
) -> None:
    service = build_decision_record_service()
    record = service.record(summary=summary, reason=reason)
    typer.echo(f"Decision recorded. [#{record.id}] {record.summary}")


@decision_app.command("list")
def list_decisions(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent decision records to show.",
    ),
) -> None:
    service = build_decision_record_service()
    records = service.list_recent(limit=limit)
    display_decision_records(records)


@app.command("help-memory")
def help_memory() -> None:
    typer.echo(
        """Alfred memory actions

WRITE

capture
  Store quick raw notes.
  Example:
    alfred capture "Milk, batteries, printer paper"

record
  Store structured durable memory, such as decisions.
  Example:
    alfred decision record --summary "Use SQLAlchemy" --reason "Easier later move to Postgres"

person add
  Register a known person in Alfred's memory.
  Example:
    alfred person add --name "Sara" --household-member

READ

search
  Search captured notes.
  Example:
    alfred search "printer"

decision list
  Review recorded decisions.
  Example:
    alfred decision list

person list
  Review known people Alfred has recorded.
  Example:
    alfred person list

remember
  Reserved for future retrieval of durable household knowledge.
  Not implemented yet.

AVOID

save
  Too generic for Alfred's memory language.
  Prefer capture or record.

LATER

don't forget
  Better suited for reminders/tasks than memory records.
  Not implemented yet.
"""
    )

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

    service = build_person_service()
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
    service = build_person_service()
    people = service.list_recent(limit=limit)
    display_people(people)


if __name__ == "__main__":
    app()