import sqlite3
from datetime import datetime, timezone

from alfred.db import SQLiteConnectionFactory


class NoteRepository:
    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def add(self, text: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()

        with self.connection_factory.get_connection() as connection:
            connection.execute(
                "INSERT INTO notes (timestamp, text) VALUES (?, ?)",
                (timestamp, text),
            )

    def list_recent(self, limit: int = 10) -> list[sqlite3.Row]:
        with self.connection_factory.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, timestamp, text
                FROM notes
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cursor.fetchall()

    def search(self, query: str, limit: int = 10) -> list[sqlite3.Row]:
        search_term = f"%{query}%"

        with self.connection_factory.get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, timestamp, text
                FROM notes
                WHERE text LIKE ? COLLATE NOCASE
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (search_term, limit),
            )
            return cursor.fetchall()
