from pathlib import Path

import pytest

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import CareInstructionRepository
from alfred.services import CareInstructionService


def test_care_instruction_service_record_saves_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Wool blanket",
        instruction="Wash on wool cycle with cold water.",
        category="Cleaning",
        details="Air dry flat to avoid stretching.",
    )

    assert care_instruction.id is not None
    assert care_instruction.subject == "Wool blanket"
    assert care_instruction.instruction == "Wash on wool cycle with cold water."
    assert care_instruction.category == "Cleaning"
    assert care_instruction.details == "Air dry flat to avoid stretching."

    care_instructions = service.list_recent(limit=10)
    assert len(care_instructions) == 1
    assert care_instructions[0].subject == "Wool blanket"
    assert (
        care_instructions[0].instruction
        == "Wash on wool cycle with cold water."
    )
    assert care_instructions[0].category == "Cleaning"
    assert care_instructions[0].details == "Air dry flat to avoid stretching."


def test_care_instruction_service_record_rejects_empty_subject(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    with pytest.raises(ValueError, match="Subject cannot be empty."):
        service.record(
            subject="   ",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )


def test_care_instruction_service_record_rejects_empty_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    with pytest.raises(ValueError, match="Instruction cannot be empty."):
        service.record(
            subject="Wool blanket",
            instruction="   ",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )


def test_care_instruction_service_record_strips_inputs(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="  Wool blanket  ",
        instruction="  Wash on wool cycle with cold water.  ",
        category="  Cleaning  ",
        details="  Air dry flat to avoid stretching.  ",
    )

    assert care_instruction.subject == "Wool blanket"
    assert care_instruction.instruction == "Wash on wool cycle with cold water."
    assert care_instruction.category == "Cleaning"
    assert care_instruction.details == "Air dry flat to avoid stretching."


def test_care_instruction_service_record_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Wool blanket",
        instruction="Wash on wool cycle with cold water.",
        category="   ",
        details="   ",
    )

    assert care_instruction.category is None
    assert care_instruction.details is None


def test_care_instruction_service_update_updates_existing_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Wool blanket",
        instruction="Wash on wool cycle with cold water.",
        category="Cleaning",
        details="Air dry flat to avoid stretching.",
    )

    updated_care_instruction = service.update(
        care_instruction_id=care_instruction.id,
        instruction="Hand wash gently in cold water.",
        category="Laundry",
        details="Do not tumble dry.",
    )

    assert updated_care_instruction.id == care_instruction.id
    assert updated_care_instruction.subject == "Wool blanket"
    assert (
        updated_care_instruction.instruction
        == "Hand wash gently in cold water."
    )
    assert updated_care_instruction.category == "Laundry"
    assert updated_care_instruction.details == "Do not tumble dry."
    assert updated_care_instruction.updated_at is not None


def test_care_instruction_service_update_rejects_missing_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    with pytest.raises(
        ValueError,
        match="Care instruction 9999 was not found.",
    ):
        service.update(
            care_instruction_id=9999,
            instruction="Hand wash gently in cold water.",
            category="Laundry",
            details="Do not tumble dry.",
        )


def test_care_instruction_service_update_rejects_retired_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Guest towels",
        instruction="Wash at 60C and tumble dry low.",
        category="Laundry",
        details=None,
    )
    service.retire(
        care_instruction_id=care_instruction.id,
        reason="Replaced by updated laundry guidance",
    )

    with pytest.raises(
        ValueError,
        match=(
            f"Care instruction {care_instruction.id} is retired "
            "and cannot be updated."
        ),
    ):
        service.update(
            care_instruction_id=care_instruction.id,
            instruction="Use a delicate cycle instead.",
            category="Laundry",
            details=None,
        )


def test_care_instruction_service_update_rejects_empty_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Wool blanket",
        instruction="Wash on wool cycle with cold water.",
        category="Cleaning",
        details="Air dry flat to avoid stretching.",
    )

    with pytest.raises(ValueError, match="Instruction cannot be empty."):
        service.update(
            care_instruction_id=care_instruction.id,
            instruction="   ",
            category="Laundry",
            details="Do not tumble dry.",
        )


def test_care_instruction_service_update_normalizes_blank_optional_fields_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Wool blanket",
        instruction="Wash on wool cycle with cold water.",
        category="Cleaning",
        details="Air dry flat to avoid stretching.",
    )

    updated_care_instruction = service.update(
        care_instruction_id=care_instruction.id,
        instruction="Hand wash gently in cold water.",
        category="   ",
        details="   ",
    )

    assert updated_care_instruction.category is None
    assert updated_care_instruction.details is None


def test_care_instruction_service_retire_retires_existing_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Guest towels",
        instruction="Wash at 60C and tumble dry low.",
        category="Laundry",
        details=None,
    )

    retired_care_instruction = service.retire(
        care_instruction_id=care_instruction.id,
        reason="Replaced by updated laundry guidance",
    )

    assert retired_care_instruction.id == care_instruction.id
    assert retired_care_instruction.retired_at is not None
    assert (
        retired_care_instruction.retired_reason
        == "Replaced by updated laundry guidance"
    )

    care_instructions = service.list_recent(limit=10)
    assert len(care_instructions) == 0


def test_care_instruction_service_retire_rejects_missing_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    with pytest.raises(
        ValueError,
        match="Care instruction 9999 was not found.",
    ):
        service.retire(
            care_instruction_id=9999,
            reason="No longer active",
        )


def test_care_instruction_service_retire_rejects_already_retired_care_instruction(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Guest towels",
        instruction="Wash at 60C and tumble dry low.",
        category="Laundry",
        details=None,
    )
    service.retire(
        care_instruction_id=care_instruction.id,
        reason="Replaced by updated laundry guidance",
    )

    with pytest.raises(
        ValueError,
        match=f"Care instruction {care_instruction.id} is already retired.",
    ):
        service.retire(
            care_instruction_id=care_instruction.id,
            reason="No longer active",
        )


def test_care_instruction_service_retire_normalizes_blank_reason_to_none(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    care_instruction = service.record(
        subject="Guest towels",
        instruction="Wash at 60C and tumble dry low.",
        category="Laundry",
        details=None,
    )

    retired_care_instruction = service.retire(
        care_instruction_id=care_instruction.id,
        reason="   ",
    )

    assert retired_care_instruction.retired_at is not None
    assert retired_care_instruction.retired_reason is None


def test_care_instruction_service_list_recent_returns_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    service.record(
        subject="First instruction",
        instruction="First step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Second instruction",
        instruction="Second step.",
        category=None,
        details=None,
    )

    care_instructions = service.list_recent(limit=10)

    assert len(care_instructions) == 2
    assert care_instructions[0].subject == "Second instruction"
    assert care_instructions[1].subject == "First instruction"


def test_care_instruction_service_list_recent_respects_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    service.record(
        subject="First instruction",
        instruction="First step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Second instruction",
        instruction="Second step.",
        category=None,
        details=None,
    )
    service.record(
        subject="Third instruction",
        instruction="Third step.",
        category=None,
        details=None,
    )

    care_instructions = service.list_recent(limit=2)

    assert len(care_instructions) == 2
    assert care_instructions[0].subject == "Third instruction"
    assert care_instructions[1].subject == "Second instruction"


def test_care_instruction_service_list_recent_uses_default_limit(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)
    service = CareInstructionService(repository)

    for index in range(12):
        service.record(
            subject=f"Instruction {index}",
            instruction=f"Step {index}.",
            category=None,
            details=None,
        )

    care_instructions = service.list_recent()

    assert len(care_instructions) == 10
    assert care_instructions[0].subject == "Instruction 11"
    assert care_instructions[-1].subject == "Instruction 2"