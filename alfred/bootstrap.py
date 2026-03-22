from pathlib import Path

from alfred.db import SQLAlchemySessionFactory
from alfred.repositories import (
    AssetRepository,
    CareInstructionRepository,
    DecisionRecordRepository,
    HouseholdFactRepository,
    NoteRepository,
    PersonRepository,
    ProcedureRepository,
    PurchaseRepository,
)
from alfred.services import (
    AssetService,
    CareInstructionService,
    DecisionRecordService,
    HouseholdFactService,
    NoteService,
    PersonService,
    ProcedureService,
    PurchaseService,
)


def get_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return data_dir

    return Path.home() / ".alfred"


def get_db_path(data_dir: Path | None = None) -> Path:
    return get_data_dir(data_dir) / "alfred.db"


def init_sqlalchemy(data_dir: Path | None = None) -> SQLAlchemySessionFactory:
    db_path = get_db_path(data_dir)
    session_factory = SQLAlchemySessionFactory(db_path)
    session_factory.create_all()
    return session_factory


def build_note_service(data_dir: Path | None = None) -> NoteService:
    session_factory = init_sqlalchemy(data_dir)
    repository = NoteRepository(session_factory)
    return NoteService(repository)


def build_decision_record_service(
    data_dir: Path | None = None,
) -> DecisionRecordService:
    session_factory = init_sqlalchemy(data_dir)
    repository = DecisionRecordRepository(session_factory)
    return DecisionRecordService(repository)


def build_person_service(data_dir: Path | None = None) -> PersonService:
    session_factory = init_sqlalchemy(data_dir)
    repository = PersonRepository(session_factory)
    return PersonService(repository)


def build_household_fact_service(
    data_dir: Path | None = None,
) -> HouseholdFactService:
    session_factory = init_sqlalchemy(data_dir)
    repository = HouseholdFactRepository(session_factory)
    return HouseholdFactService(repository)


def build_asset_service(data_dir: Path | None = None) -> AssetService:
    session_factory = init_sqlalchemy(data_dir)
    repository = AssetRepository(session_factory)
    return AssetService(repository)


def build_purchase_service(data_dir: Path | None = None) -> PurchaseService:
    session_factory = init_sqlalchemy(data_dir)
    repository = PurchaseRepository(session_factory)
    return PurchaseService(repository)


def build_care_instruction_service(
    data_dir: Path | None = None,
) -> CareInstructionService:
    session_factory = init_sqlalchemy(data_dir)
    repository = CareInstructionRepository(session_factory)
    return CareInstructionService(repository)


def build_procedure_service(
    data_dir: Path | None = None,
) -> ProcedureService:
    session_factory = init_sqlalchemy(data_dir)
    repository = ProcedureRepository(session_factory)
    return ProcedureService(repository)