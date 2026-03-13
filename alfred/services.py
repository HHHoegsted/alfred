from datetime import datetime

def format_timestamp(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M UTC")

class NoteService:

	def __init__(self, note_repository):
		self.note_repository = note_repository
	
	def capture(self, text: str):
		self.note_repository.add(text)
	
	def list_recent(self, limit: int = 10):
		return self.note_repository.list_recent(limit=limit)