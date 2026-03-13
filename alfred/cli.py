import typer
from pathlib import Path

from alfred.db import SQLiteConnectionFactory
from alfred.repositories import NoteRepository
from alfred.services import NoteService, format_timestamp

app = typer.Typer()

def get_data_dir() -> Path:
	data_dir = Path.home() / ".alfred"
	data_dir.mkdir(parents=True, exist_ok=True)
	return data_dir

def build_note_service():

	db_path = get_data_dir() / "alfred.db"

	db = SQLiteConnectionFactory(db_path)
	db.init_db()

	repo = NoteRepository(db)

	return NoteService(repo)

@app.command()
def hello() -> None:
	typer.echo("Alfred is alive")

@app.command()
def capture(text: str) -> None:
	cleaned_text = text.strip()
	if not cleaned_text:
		raise typer.BadParameter("Note cannot be empty.")
	
	service = build_note_service()
	service.capture(text)
	typer.echo("Note saved.")

@app.command("list")
def list_notes(limit: int = 10) -> None:
	if limit < 1:
		raise typer.BadParameter("Limit must be at least 1.")
	service = build_note_service()
	notes = service.list_recent(limit=limit)

	if not notes:
		typer.echo("No notes found.")
		return

	for note in notes:
		pretty_timestamp = format_timestamp(note["timestamp"])

		typer.echo(f"[{note['id']}] {pretty_timestamp}")
		typer.echo(f"	{note['text']}")
		typer.echo()