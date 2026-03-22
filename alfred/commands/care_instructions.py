import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import CareInstruction


care_instruction_app = typer.Typer(help="Record and review care instructions.")


def display_care_instructions(care_instructions: list[CareInstruction]) -> None:
    for care_instruction in care_instructions:
        pretty_timestamp = format_timestamp(care_instruction.created_at.isoformat())
        typer.echo(f"[{care_instruction.id}] {pretty_timestamp}")
        typer.echo(f"  Subject: {care_instruction.subject}")
        typer.echo(f"  Instruction: {care_instruction.instruction}")

        if care_instruction.category:
            typer.echo(f"  Category: {care_instruction.category}")

        if care_instruction.details:
            typer.echo(f"  Details: {care_instruction.details}")

        typer.echo()


@care_instruction_app.command("add")
def add(
    subject: str = typer.Option(..., "--subject", help="What the care instruction is about."),
    instruction: str = typer.Option(..., "--instruction", help="The care instruction itself."),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional category for the care instruction.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional extra context for the care instruction.",
    ),
) -> None:
    service = bootstrap.build_care_instruction_service()

    try:
        care_instruction = service.record(
            subject=subject,
            instruction=instruction,
            category=category,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Care instruction recorded.")
    typer.echo(f"[{care_instruction.id}] {care_instruction.subject}")


@care_instruction_app.command("update")
def update(
    care_instruction_id: int = typer.Argument(
        ...,
        help="The ID of the care instruction to update.",
    ),
    instruction: str = typer.Option(..., "--instruction", help="The updated care instruction."),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Optional updated category for the care instruction.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional updated extra context for the care instruction.",
    ),
) -> None:
    service = bootstrap.build_care_instruction_service()

    try:
        care_instruction = service.update(
            care_instruction_id=care_instruction_id,
            instruction=instruction,
            category=category,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Care instruction updated.")
    typer.echo(f"[{care_instruction.id}] {care_instruction.subject}")


@care_instruction_app.command("retire")
def retire(
    care_instruction_id: int = typer.Argument(
        ...,
        help="The ID of the care instruction to retire.",
    ),
    reason: str | None = typer.Option(
        None,
        "--reason",
        help="Optional reason the care instruction is no longer active.",
    ),
) -> None:
    service = bootstrap.build_care_instruction_service()

    try:
        care_instruction = service.retire(
            care_instruction_id=care_instruction_id,
            reason=reason,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo("Care instruction retired.")
    typer.echo(f"[{care_instruction.id}] {care_instruction.subject}")


@care_instruction_app.command("list")
def list_care_instructions(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent care instructions to show.",
    ),
) -> None:
    service = bootstrap.build_care_instruction_service()
    care_instructions: list[CareInstruction] = service.list_recent(limit=limit)

    if not care_instructions:
        typer.echo("No care instructions found.")
        return

    display_care_instructions(care_instructions)
