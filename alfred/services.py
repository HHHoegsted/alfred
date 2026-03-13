import sqlite3
from datetime import datetime

from alfred.repositories import NoteRepository


def format_timestamp(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


class NoteService:
    def __init__(self, note_repository: NoteRepository) -> None:
        self.note_repository = note_repository

    def capture(self, text: str) -> None:
        self.note_repository.add(text)

    def list_recent(self, limit: int = 10) -> list[sqlite3.Row]:
        return self.note_repository.list_recent(limit=limit)

    def search(self, query: str, limit: int = 10) -> list[sqlite3.Row]:
        return self.note_repository.search(query=query, limit=limit)
