from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import CareInstruction
from alfred.repositories import CareInstructionRepository


def test_care_instruction_repository_create_and_list_recent(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )

        assert created.id is not None
        assert created.created_at is not None
        assert created.subject == "Wool blanket"
        assert created.instruction == "Wash on wool cycle with cold water."
        assert created.category == "Cleaning"
        assert created.details == "Air dry flat to avoid stretching."

        care_instructions = repository.list_recent(limit=10)

        assert len(care_instructions) == 1
        assert care_instructions[0].id == created.id
        assert care_instructions[0].subject == "Wool blanket"
        assert (
            care_instructions[0].instruction
            == "Wash on wool cycle with cold water."
        )
        assert care_instructions[0].category == "Cleaning"
        assert care_instructions[0].details == "Air dry flat to avoid stretching."
    finally:
        session_factory.close()


def test_care_instruction_repository_get_by_id_returns_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )

        care_instruction = repository.get_by_id(created.id)

        assert care_instruction is not None
        assert care_instruction.id == created.id
        assert care_instruction.subject == "Wool blanket"
        assert care_instruction.instruction == "Wash on wool cycle with cold water."
        assert care_instruction.category == "Cleaning"
        assert care_instruction.details == "Air dry flat to avoid stretching."
    finally:
        session_factory.close()


def test_care_instruction_repository_get_by_id_returns_none_for_missing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        care_instruction = repository.get_by_id(9999)

        assert care_instruction is None
    finally:
        session_factory.close()


def test_care_instruction_repository_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        repository.create(
            subject="First instruction",
            instruction="First step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Second instruction",
            instruction="Second step.",
            category=None,
            details=None,
        )

        care_instructions = repository.list_recent(limit=10)

        assert len(care_instructions) == 2
        assert care_instructions[0].subject == "Second instruction"
        assert care_instructions[1].subject == "First instruction"
    finally:
        session_factory.close()


def test_care_instruction_repository_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        repository.create(
            subject="First instruction",
            instruction="First step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Second instruction",
            instruction="Second step.",
            category=None,
            details=None,
        )
        repository.create(
            subject="Third instruction",
            instruction="Third step.",
            category=None,
            details=None,
        )

        care_instructions = repository.list_recent(limit=2)

        assert len(care_instructions) == 2
        assert care_instructions[0].subject == "Third instruction"
        assert care_instructions[1].subject == "Second instruction"
    finally:
        session_factory.close()


def test_care_instruction_repository_update_updates_existing_record(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )

        updated = repository.update(
            care_instruction=created,
            instruction="Hand wash gently in cold water.",
            category="Laundry",
            details="Do not tumble dry.",
        )

        assert updated is not None
        assert updated.id == created.id
        assert updated.subject == "Wool blanket"
        assert updated.instruction == "Hand wash gently in cold water."
        assert updated.category == "Laundry"
        assert updated.details == "Do not tumble dry."
        assert updated.updated_at is not None
    finally:
        session_factory.close()


def test_care_instruction_repository_update_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )

        with session_factory.get_session() as session:
            persisted = session.get(CareInstruction, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        updated = repository.update(
            care_instruction=created,
            instruction="Hand wash gently in cold water.",
            category="Laundry",
            details="Do not tumble dry.",
        )

        assert updated is created
        assert updated.id == created.id
        assert updated.instruction == "Wash on wool cycle with cold water."
        assert updated.category == "Cleaning"
        assert updated.details == "Air dry flat to avoid stretching."
        assert updated.updated_at is None
    finally:
        session_factory.close()


def test_care_instruction_repository_retire_marks_record_as_retired(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Guest towels",
            instruction="Wash at 60C and tumble dry low.",
            category="Laundry",
            details=None,
        )

        retired = repository.retire(
            care_instruction=created,
            reason="Replaced by updated laundry guidance",
        )

        assert retired is not None
        assert retired.id == created.id
        assert retired.retired_at is not None
        assert retired.retired_reason == "Replaced by updated laundry guidance"

        care_instructions = repository.list_recent(limit=10)
        assert len(care_instructions) == 0
    finally:
        session_factory.close()


def test_care_instruction_repository_retire_returns_input_when_record_missing(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    try:
        created = repository.create(
            subject="Guest towels",
            instruction="Wash at 60C and tumble dry low.",
            category="Laundry",
            details=None,
        )

        with session_factory.get_session() as session:
            persisted = session.get(CareInstruction, created.id)
            assert persisted is not None
            session.delete(persisted)
            session.commit()

        retired = repository.retire(
            care_instruction=created,
            reason="Replaced by updated laundry guidance",
        )

        assert retired is created
        assert retired.id == created.id
        assert retired.retired_at is None
        assert retired.retired_reason is None
    finally:
        session_factory.close()