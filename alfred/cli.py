import typer
from datetime import datetime
from pathlib import Path

from alfred.db import SQLiteConnectionFactory
from alfred.repositories import NoteRepository
from alfred.services import NoteService

app = typer.Typer()

def build_note_service():

	db = SQLiteConnectionFactory(Path("data/alfred.db"))
	db.init_db()

	repo = NoteRepository(db)

	return NoteService(repo)

@app.command()
def hello() -> None:
	print("Alfred is alive")

@app.command()
def capture(text: str) -> None:
	service = build_note_service()
	service.capture(text)
	print("Note saved.")

@app.command("list")
def list_notes(limit: int = 10) -> None:
	service = build_note_service()
	notes = service.list_recent(limit=limit)

	if not notes:
		print("No notes found.")
		return

	for note in notes:
		timestamp = datetime.fromisoformat(note["timestamp"])
		pretty_timestamp = timestamp.strftime("%Y-%m-%d %H:%M UTC")

		print(f"[{note['id']}] {pretty_timestamp}")
		print(f"	{note['text']}")
		print()