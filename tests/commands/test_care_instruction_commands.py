from pathlib import Path

import alfred.commands.care_instructions as care_instruction_commands
from typer.testing import CliRunner

from alfred import cli


runner = CliRunner()


def test_care_add_records_care_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "care",
            "add",
            "--subject",
            "Wool blanket",
            "--instruction",
            "Wash on wool cycle with cold water.",
            "--category",
            "Cleaning",
            "--details",
            "Air dry flat to avoid stretching.",
        ],
    )

    assert result.exit_code == 0
    assert "Care instruction recorded." in result.stdout
    assert "[1] Wool blanket" in result.stdout

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        care_instructions = service.list_recent(limit=10)

        assert len(care_instructions) == 1
        assert care_instructions[0].subject == "Wool blanket"
        assert care_instructions[0].instruction == "Wash on wool cycle with cold water."
        assert care_instructions[0].category == "Cleaning"
        assert care_instructions[0].details == "Air dry flat to avoid stretching."
    finally:
        service.repository.session_factory.close()


def test_care_add_rejects_blank_subject(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "care",
            "add",
            "--subject",
            "   ",
            "--instruction",
            "Wash on wool cycle with cold water.",
        ],
    )

    assert result.exit_code != 0
    assert "Subject cannot be empty." in result.stdout


def test_care_add_rejects_blank_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "care",
            "add",
            "--subject",
            "Wool blanket",
            "--instruction",
            "   ",
        ],
    )

    assert result.exit_code != 0
    assert "Instruction cannot be empty." in result.stdout


def test_care_update_updates_existing_care_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        care_instruction = service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )

        result = runner.invoke(
            cli.app,
            [
                "care",
                "update",
                str(care_instruction.id),
                "--instruction",
                "Hand wash gently in cold water.",
                "--category",
                "Laundry",
                "--details",
                "Do not tumble dry.",
            ],
        )

        assert result.exit_code == 0
        assert "Care instruction updated." in result.stdout
        assert f"[{care_instruction.id}] Wool blanket" in result.stdout
    finally:
        service.repository.session_factory.close()

    refreshed_service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        care_instructions = refreshed_service.list_recent(limit=10)

        assert len(care_instructions) == 1
        assert care_instructions[0].id == care_instruction.id
        assert care_instructions[0].subject == "Wool blanket"
        assert care_instructions[0].instruction == "Hand wash gently in cold water."
        assert care_instructions[0].category == "Laundry"
        assert care_instructions[0].details == "Do not tumble dry."
    finally:
        refreshed_service.repository.session_factory.close()


def test_care_update_rejects_blank_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        care_instruction = service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
        )

        result = runner.invoke(
            cli.app,
            [
                "care",
                "update",
                str(care_instruction.id),
                "--instruction",
                "   ",
            ],
        )

        assert result.exit_code != 0
        assert "Instruction cannot be empty." in result.stdout
    finally:
        service.repository.session_factory.close()


def test_care_update_rejects_missing_care_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "care",
            "update",
            "9999",
            "--instruction",
            "Hand wash gently in cold water.",
        ],
    )

    assert result.exit_code != 0
    assert "Care instruction 9999 was not found." in result.stdout


def test_care_retire_retires_existing_care_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        care_instruction = service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
        )

        result = runner.invoke(
            cli.app,
            [
                "care",
                "retire",
                str(care_instruction.id),
                "--reason",
                "Replaced by updated manufacturer guidance.",
            ],
        )

        assert result.exit_code == 0
        assert "Care instruction retired." in result.stdout
        assert f"[{care_instruction.id}] Wool blanket" in result.stdout
    finally:
        service.repository.session_factory.close()

    verification_service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        stored_care_instruction = verification_service.repository.get_by_id(
            care_instruction.id
        )
        assert stored_care_instruction is not None
        assert stored_care_instruction.retired_at is not None
        assert (
            stored_care_instruction.retired_reason
            == "Replaced by updated manufacturer guidance."
        )
    finally:
        verification_service.repository.session_factory.close()


def test_care_retire_rejects_missing_care_instruction(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(
        cli.app,
        [
            "care",
            "retire",
            "9999",
        ],
    )

    assert result.exit_code != 0
    assert "Care instruction 9999 was not found." in result.stdout


def test_care_list_shows_care_instructions(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
            category="Cleaning",
            details="Air dry flat to avoid stretching.",
        )
        service.record(
            subject="Coffee grinder",
            instruction="Brush burrs weekly and keep dry.",
            category="Maintenance",
            details="Do not rinse with water.",
        )

        result = runner.invoke(cli.app, ["care", "list"])

        assert result.exit_code == 0
        assert "Wool blanket" in result.stdout
        assert "Coffee grinder" in result.stdout
        assert "Category: Cleaning" in result.stdout
        assert "Category: Maintenance" in result.stdout
    finally:
        service.repository.session_factory.close()


def test_care_list_shows_no_care_instructions_message_when_empty(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    result = runner.invoke(cli.app, ["care", "list"])

    assert result.exit_code == 0
    assert "No care instructions found." in result.stdout


def test_care_list_respects_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
        )
        service.record(
            subject="Coffee grinder",
            instruction="Brush burrs weekly and keep dry.",
        )

        result = runner.invoke(cli.app, ["care", "list", "--limit", "1"])

        assert result.exit_code == 0
        assert "Coffee grinder" in result.stdout
        assert "Wool blanket" not in result.stdout
    finally:
        service.repository.session_factory.close()


def test_care_list_accepts_short_limit_alias(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original_build_care_instruction_service = (
        care_instruction_commands.bootstrap.build_care_instruction_service
    )

    def build_care_instruction_service_for_test():
        return original_build_care_instruction_service(data_dir=tmp_path)

    monkeypatch.setattr(
        care_instruction_commands.bootstrap,
        "build_care_instruction_service",
        build_care_instruction_service_for_test,
    )

    service = original_build_care_instruction_service(data_dir=tmp_path)
    try:
        service.record(
            subject="Wool blanket",
            instruction="Wash on wool cycle with cold water.",
        )
        service.record(
            subject="Coffee grinder",
            instruction="Brush burrs weekly and keep dry.",
        )

        result = runner.invoke(cli.app, ["care", "list", "-n", "1"])

        assert result.exit_code == 0
        assert "Coffee grinder" in result.stdout
        assert "Wool blanket" not in result.stdout
    finally:
        service.repository.session_factory.close()