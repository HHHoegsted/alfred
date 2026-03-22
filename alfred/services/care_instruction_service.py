from alfred.models import CareInstruction
from alfred.repositories import CareInstructionRepository


class CareInstructionService:
    def __init__(self, repository: CareInstructionRepository) -> None:
        self.repository = repository

    def record(
        self,
        subject: str,
        instruction: str,
        category: str | None = None,
        details: str | None = None,
    ) -> CareInstruction:
        subject = subject.strip()
        instruction = instruction.strip()
        category = category.strip() if category is not None else None
        details = details.strip() if details is not None else None

        if not subject:
            raise ValueError("Subject cannot be empty.")

        if not instruction:
            raise ValueError("Instruction cannot be empty.")

        if category == "":
            category = None

        if details == "":
            details = None

        return self.repository.create(
            subject=subject,
            category=category,
            instruction=instruction,
            details=details,
        )

    def update(
        self,
        care_instruction_id: int,
        instruction: str,
        category: str | None = None,
        details: str | None = None,
    ) -> CareInstruction:
        care_instruction = self.repository.get_by_id(care_instruction_id)
        if care_instruction is None:
            raise ValueError(
                f"Care instruction {care_instruction_id} was not found."
            )

        if care_instruction.retired_at is not None:
            raise ValueError(
                f"Care instruction {care_instruction_id} is retired and cannot be updated."
            )

        instruction = instruction.strip()
        category = category.strip() if category is not None else None
        details = details.strip() if details is not None else None

        if not instruction:
            raise ValueError("Instruction cannot be empty.")

        if category == "":
            category = None

        if details == "":
            details = None

        return self.repository.update(
            care_instruction,
            category=category,
            instruction=instruction,
            details=details,
        )

    def retire(
        self,
        care_instruction_id: int,
        reason: str | None = None,
    ) -> CareInstruction:
        care_instruction = self.repository.get_by_id(care_instruction_id)
        if care_instruction is None:
            raise ValueError(
                f"Care instruction {care_instruction_id} was not found."
            )

        if care_instruction.retired_at is not None:
            raise ValueError(
                f"Care instruction {care_instruction_id} is already retired."
            )

        reason = reason.strip() if reason is not None else None
        if reason == "":
            reason = None

        return self.repository.retire(
            care_instruction,
            reason=reason,
        )

    def list_recent(self, limit: int = 10) -> list[CareInstruction]:
        return self.repository.list_recent(limit=limit)