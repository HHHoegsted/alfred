from alfred.models import Procedure
from alfred.repositories import ProcedureRepository


class ProcedureService:
    def __init__(self, repository: ProcedureRepository) -> None:
        self.repository = repository

    def record(
        self,
        subject: str,
        procedure: str,
        category: str | None = None,
        details: str | None = None,
    ) -> Procedure:
        subject = subject.strip()
        procedure = procedure.strip()
        category = category.strip() if category is not None else None
        details = details.strip() if details is not None else None

        if not subject:
            raise ValueError("Subject cannot be empty.")

        if not procedure:
            raise ValueError("Procedure cannot be empty.")

        if category == "":
            category = None

        if details == "":
            details = None

        return self.repository.create(
            subject=subject,
            category=category,
            procedure=procedure,
            details=details,
        )

    def update(
        self,
        procedure_id: int,
        procedure: str,
        category: str | None = None,
        details: str | None = None,
    ) -> Procedure:
        procedure_record = self.repository.get_by_id(procedure_id)
        if procedure_record is None:
            raise ValueError(f"Procedure {procedure_id} was not found.")

        if procedure_record.retired_at is not None:
            raise ValueError(
                f"Procedure {procedure_id} is retired and cannot be updated."
            )

        procedure = procedure.strip()
        category = category.strip() if category is not None else None
        details = details.strip() if details is not None else None

        if not procedure:
            raise ValueError("Procedure cannot be empty.")

        if category == "":
            category = None

        if details == "":
            details = None

        return self.repository.update(
            procedure_record,
            category=category,
            procedure=procedure,
            details=details,
        )

    def retire(
        self,
        procedure_id: int,
        reason: str | None = None,
    ) -> Procedure:
        procedure_record = self.repository.get_by_id(procedure_id)
        if procedure_record is None:
            raise ValueError(f"Procedure {procedure_id} was not found.")

        if procedure_record.retired_at is not None:
            raise ValueError(f"Procedure {procedure_id} is already retired.")

        reason = reason.strip() if reason is not None else None
        if reason == "":
            reason = None

        return self.repository.retire(
            procedure_record,
            reason=reason,
        )

    def list_recent(self, limit: int = 10) -> list[Procedure]:
        return self.repository.list_recent(limit=limit)