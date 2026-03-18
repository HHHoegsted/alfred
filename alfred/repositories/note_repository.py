from sqlalchemy import select

from alfred.models import Note


class NoteRepository:
    def __init__(self, session) -> None:
        self.session = session

    def add(self, text: str) -> Note:
        note = Note(text=text)
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def list_recent(self, limit: int = 10) -> list[Note]:
        statement = select(Note).order_by(Note.created_at.desc(), Note.id.desc()).limit(limit)
        return list(self.session.scalars(statement))

    def search(self, query: str, limit: int = 10) -> list[Note]:
        statement = (
            select(Note)
            .where(Note.text.ilike(f"%{query}%"))
            .order_by(Note.created_at.desc(), Note.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))