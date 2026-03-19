from sqlalchemy import select

from alfred.models import Note


class NoteRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def add(self, text: str) -> Note:
        with self.session_factory.get_session() as session:
            note = Note(text=text)
            session.add(note)
            session.commit()
            session.refresh(note)
            return note

    def list_recent(self, limit: int = 10) -> list[Note]:
        statement = (
            select(Note)
            .order_by(Note.created_at.desc(), Note.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))

    def search(self, query: str, limit: int = 10) -> list[Note]:
        statement = (
            select(Note)
            .where(Note.text.ilike(f"%{query}%"))
            .order_by(Note.created_at.desc(), Note.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))