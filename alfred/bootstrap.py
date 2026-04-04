from pathlib import Path
from typing import TypeVar

from alfred.db import SQLAlchemySessionFactory
from alfred.repositories import (
    AssetRepository,
    CareInstructionRepository,
    DecisionRecordRepository,
    HouseholdFactRepository,
    MaintenanceRecordRepository,
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
    MaintenanceRecordService,
    NoteService,
    PersonService,
    ProcedureService,
    PurchaseService,
)


RepositoryT = TypeVar("RepositoryT")
ServiceT = TypeVar("ServiceT")


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


def _build_service(
    data_dir: Path | None,
    repository_cls: type[RepositoryT],
    service_cls: type[ServiceT],
) -> ServiceT:
    session_factory = init_sqlalchemy(data_dir)
    repository = repository_cls(session_factory)
    return service_cls(repository)


def build_note_service(data_dir: Path | None = None) -> NoteService:
    return _build_service(data_dir, NoteRepository, NoteService)


def build_decision_record_service(
    data_dir: Path | None = None,
) -> DecisionRecordService:
    return _build_service(
        data_dir,
        DecisionRecordRepository,
        DecisionRecordService,
    )


def build_person_service(data_dir: Path | None = None) -> PersonService:
    return _build_service(data_dir, PersonRepository, PersonService)


def build_household_fact_service(
    data_dir: Path | None = None,
) -> HouseholdFactService:
    return _build_service(
        data_dir,
        HouseholdFactRepository,
        HouseholdFactService,
    )


def build_asset_service(data_dir: Path | None = None) -> AssetService:
    return _build_service(data_dir, AssetRepository, AssetService)


def build_purchase_service(data_dir: Path | None = None) -> PurchaseService:
    return _build_service(data_dir, PurchaseRepository, PurchaseService)


def build_care_instruction_service(
    data_dir: Path | None = None,
) -> CareInstructionService:
    return _build_service(
        data_dir,
        CareInstructionRepository,
        CareInstructionService,
    )


def build_procedure_service(
    data_dir: Path | None = None,
) -> ProcedureService:
    return _build_service(data_dir, ProcedureRepository, ProcedureService)


def build_maintenance_record_service(
    data_dir: Path | None = None,
) -> MaintenanceRecordService:
    return _build_service(
        data_dir,
        MaintenanceRecordRepository,
        MaintenanceRecordService,
    )