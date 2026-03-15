from sqlalchemy import select
from sqlalchemy.orm import Session

from alfred.models import Note


class NoteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, text: str) -> None:
        note = Note(text=text)
        self.session.add(note)
        self.session.commit()

    def list_recent(self, limit: int = 10) -> list[Note]:
        statement = (
            select(Note)
            .order_by(Note.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def search(self, query: str, limit: int = 10) -> list[Note]:
        statement = (
            select(Note)
            .where(Note.text.ilike(f"%{query}%"))
            .order_by(Note.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())