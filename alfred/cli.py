import sqlite3
from pathlib import Path

import typer

from alfred.db import SQLiteConnectionFactory
from alfred.repositories import NoteRepository
from alfred.services import NoteService, format_timestamp

app = typer.Typer(help="Alfred is a local-first CLI for capturing and reviewing notes.")


def display_notes(notes: list[sqlite3.Row]) -> None:
    for note in notes:
        pretty_timestamp = format_timestamp(note["timestamp"])
        typer.echo(f"[{note['id']}] {pretty_timestamp}")
        typer.echo(f"    {note['text']}")
        typer.echo()


def get_data_dir() -> Path:
    data_dir = Path.home() / ".alfred"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def build_note_service() -> NoteService:
    db_path = get_data_dir() / "alfred.db"
    db = SQLiteConnectionFactory(db_path)
    db.init_db()
    repo = NoteRepository(db)
    return NoteService(repo)


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
    typer.echo("Note saved.")


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
