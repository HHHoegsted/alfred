from pathlib import Path

from alfred.db import SQLiteConnectionFactory, SQLAlchemySessionFactory
from alfred.repositories import DecisionRecordRepository, NoteRepository
from alfred.services import DecisionRecordService, NoteService


def get_data_dir() -> Path:
    data_dir = Path.home() / ".alfred"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_db_path(data_dir: Path | None = None) -> Path:
    base_dir = data_dir or get_data_dir()
    return base_dir / "alfred.db"


def build_note_service(data_dir: Path | None = None) -> NoteService:
    db_path = get_db_path(data_dir)

    sqlite_db = SQLiteConnectionFactory(db_path)
    sqlite_db.init_db()

    return NoteService(NoteRepository(sqlite_db))


def init_sqlalchemy(data_dir: Path | None = None) -> SQLAlchemySessionFactory:
    import alfred.models

    session_factory = SQLAlchemySessionFactory(get_db_path(data_dir))
    session_factory.create_all()
    return session_factory


def build_decision_record_service(
    data_dir: Path | None = None,
) -> DecisionRecordService:
    session_factory = init_sqlalchemy(data_dir=data_dir)
    session = session_factory.get_session()
    repository = DecisionRecordRepository(session)
    return DecisionRecordService(repository)