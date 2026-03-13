from datetime import datetime, timezone

class NoteRepository:

	def __init__(self, connection_factory):
		self.connection_factory = connection_factory

	def add(self, text: str):
		timestamp = datetime.now(timezone.utc).isoformat()

		with self.connection_factory.get_connection() as connection:
			connection.execute(
				"INSERT INTO notes (timestamp, text) VALUES (? ,?)",
				(timestamp, text)
			)

	def list_recent(self, limit: int = 10):
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