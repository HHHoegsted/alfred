from alfred.models import Note
from alfred.repositories import NoteRepository


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def capture(self, text: str) -> Note:
        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError("Note cannot be empty.")

        return self.repository.add(cleaned_text)

    def list_recent(self, limit: int = 20) -> list[Note]:
        return self.repository.list_recent(limit=limit)

    def search(self, query: str, limit: int = 20) -> list[Note]:
        return self.repository.search(query=query, limit=limit)