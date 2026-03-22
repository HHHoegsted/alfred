from datetime import UTC, datetime

from sqlalchemy import select

from alfred.models import CareInstruction


class CareInstructionRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        subject: str,
        category: str | None,
        instruction: str,
        details: str | None,
    ) -> CareInstruction:
        with self.session_factory.get_session() as session:
            care_instruction = CareInstruction(
                subject=subject,
                category=category,
                instruction=instruction,
                details=details,
            )
            session.add(care_instruction)
            session.commit()
            session.refresh(care_instruction)
            return care_instruction

    def get_by_id(self, care_instruction_id: int) -> CareInstruction | None:
        statement = select(CareInstruction).where(
            CareInstruction.id == care_instruction_id
        )

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def update(
        self,
        care_instruction: CareInstruction,
        *,
        category: str | None,
        instruction: str,
        details: str | None,
    ) -> CareInstruction:
        with self.session_factory.get_session() as session:
            persisted_care_instruction = session.get(
                CareInstruction,
                care_instruction.id,
            )

            if persisted_care_instruction is None:
                return care_instruction

            persisted_care_instruction.category = category
            persisted_care_instruction.instruction = instruction
            persisted_care_instruction.details = details
            persisted_care_instruction.updated_at = datetime.now(UTC)

            session.add(persisted_care_instruction)
            session.commit()
            session.refresh(persisted_care_instruction)
            return persisted_care_instruction

    def retire(
        self,
        care_instruction: CareInstruction,
        *,
        reason: str | None,
    ) -> CareInstruction:
        with self.session_factory.get_session() as session:
            persisted_care_instruction = session.get(
                CareInstruction,
                care_instruction.id,
            )

            if persisted_care_instruction is None:
                return care_instruction

            persisted_care_instruction.retired_at = datetime.now(UTC)
            persisted_care_instruction.retired_reason = reason

            session.add(persisted_care_instruction)
            session.commit()
            session.refresh(persisted_care_instruction)
            return persisted_care_instruction

    def list_recent(self, limit: int = 10) -> list[CareInstruction]:
        statement = (
            select(CareInstruction)
            .where(CareInstruction.retired_at.is_(None))
            .order_by(CareInstruction.created_at.desc(), CareInstruction.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))