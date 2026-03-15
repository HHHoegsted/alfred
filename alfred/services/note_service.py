import sqlite3

from alfred.repositories import NoteRepository


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def capture(self, text: str) -> None:
        self.repository.add(text=text)

    def list_recent(self, limit: int = 10) -> list[sqlite3.Row]:
        return self.repository.list_recent(limit=limit)

    def search(self, query: str, limit: int = 10) -> list[sqlite3.Row]:
        return self.repository.search(query=query, limit=limit)