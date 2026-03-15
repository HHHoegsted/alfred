import typer

import alfred.cli as cli
from alfred.common import format_timestamp
from alfred.models import Note


notes_app = typer.Typer(help="Capture and review notes.")


def display_notes(notes: list[Note]) -> None:
    for note in notes:
        pretty_timestamp = format_timestamp(note.created_at.isoformat())
        typer.echo(f"[{note.id}] {pretty_timestamp}")
        typer.echo(f"  {note.text}")
        typer.echo()


@notes_app.command("capture")
def capture(
    text: str = typer.Argument(..., help="The note text to save."),
) -> None:
    cleaned_text = text.strip()
    if not cleaned_text:
        typer.echo("Note cannot be empty.")
        raise typer.Exit(code=1)

    service = cli.build_note_service()
    service.capture(cleaned_text)
    typer.echo("Note captured.")


@notes_app.command("list")
def list_notes(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent notes to show.",
    ),
) -> None:
    service = cli.build_note_service()
    notes: list[Note] = service.list_recent(limit=limit)

    if not notes:
        typer.echo("No notes found.")
        return

    display_notes(notes)


@notes_app.command("search")
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
        typer.echo("Search query cannot be empty.")
        raise typer.Exit(code=1)

    service = cli.build_note_service()
    notes: list[Note] = service.search(query=cleaned_query, limit=limit)

    if not notes:
        typer.echo("No matching notes found.")
        return

    display_notes(notes)