from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.repositories import CareInstructionRepository


def test_create_saves_care_instruction(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    care_instruction = repository.create(
        subject="Wool blanket",
        category="Cleaning",
        instruction="Wash on wool cycle with cold water.",
        details="Air dry flat to avoid stretching.",
    )

    assert care_instruction.id is not None
    assert care_instruction.subject == "Wool blanket"
    assert care_instruction.category == "Cleaning"
    assert care_instruction.instruction == "Wash on wool cycle with cold water."
    assert care_instruction.details == "Air dry flat to avoid stretching."
    assert care_instruction.created_at is not None
    assert care_instruction.updated_at is None
    assert care_instruction.retired_at is None
    assert care_instruction.retired_reason is None


def test_get_by_id_returns_care_instruction(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    created = repository.create(
        subject="Coffee grinder",
        category="Maintenance",
        instruction="Brush burrs weekly and keep dry.",
        details="Do not rinse with water.",
    )

    fetched = repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.subject == "Coffee grinder"
    assert fetched.category == "Maintenance"
    assert fetched.instruction == "Brush burrs weekly and keep dry."
    assert fetched.details == "Do not rinse with water."


def test_get_by_id_returns_none_when_missing(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    fetched = repository.get_by_id(9999)

    assert fetched is None


def test_update_updates_existing_care_instruction(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    created = repository.create(
        subject="Wool blanket",
        category="Cleaning",
        instruction="Wash on wool cycle with cold water.",
        details="Air dry flat to avoid stretching.",
    )

    updated = repository.update(
        created,
        category="Laundry",
        instruction="Hand wash gently in cold water.",
        details="Do not tumble dry.",
    )

    assert updated.id == created.id
    assert updated.subject == "Wool blanket"
    assert updated.category == "Laundry"
    assert updated.instruction == "Hand wash gently in cold water."
    assert updated.details == "Do not tumble dry."
    assert updated.updated_at is not None

    fetched = repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.category == "Laundry"
    assert fetched.instruction == "Hand wash gently in cold water."
    assert fetched.details == "Do not tumble dry."
    assert fetched.updated_at is not None


def test_retire_marks_care_instruction_as_retired(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    created = repository.create(
        subject="Guest towels",
        category="Laundry",
        instruction="Wash at 60C and tumble dry low.",
        details=None,
    )

    retired = repository.retire(
        created,
        reason="Replaced by updated laundry guidance.",
    )

    assert retired.id == created.id
    assert retired.retired_at is not None
    assert retired.retired_reason == "Replaced by updated laundry guidance."

    fetched = repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.retired_at is not None
    assert fetched.retired_reason == "Replaced by updated laundry guidance."


def test_list_recent_returns_only_active_care_instructions_newest_first(
    tmp_path: Path,
) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    first = repository.create(
        subject="First instruction",
        category=None,
        instruction="First step.",
        details=None,
    )
    second = repository.create(
        subject="Second instruction",
        category=None,
        instruction="Second step.",
        details=None,
    )
    third = repository.create(
        subject="Third instruction",
        category=None,
        instruction="Third step.",
        details=None,
    )

    repository.retire(
        second,
        reason="No longer relevant.",
    )

    care_instructions = repository.list_recent(limit=10)

    assert [care_instruction.id for care_instruction in care_instructions] == [
        third.id,
        first.id,
    ]


def test_list_recent_respects_limit(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)
    repository = CareInstructionRepository(session_factory)

    repository.create(
        subject="First instruction",
        category=None,
        instruction="First step.",
        details=None,
    )
    second = repository.create(
        subject="Second instruction",
        category=None,
        instruction="Second step.",
        details=None,
    )
    third = repository.create(
        subject="Third instruction",
        category=None,
        instruction="Third step.",
        details=None,
    )

    care_instructions = repository.list_recent(limit=2)

    assert len(care_instructions) == 2
    assert [care_instruction.id for care_instruction in care_instructions] == [
        third.id,
        second.id,
    ]