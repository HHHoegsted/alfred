import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp
from alfred.models import Reminder


reminder_app = typer.Typer(help="Record and review reminders.")


def display_reminders(reminders: list[Reminder]) -> None:
    for reminder in reminders:
        pretty_timestamp = format_timestamp(reminder.created_at.isoformat())
        typer.echo(f"[{reminder.id}] {pretty_timestamp}")
        typer.echo(f"  Title: {reminder.title}")

        if reminder.cadence:
            typer.echo(f"  Cadence: {reminder.cadence}")

        if reminder.details:
            typer.echo(f"  Details: {reminder.details}")

        typer.echo()


@reminder_app.command("add")
def add(
    title: str = typer.Option(
        ...,
        "--title",
        help="What the reminder is about.",
    ),
    cadence: str | None = typer.Option(
        None,
        "--cadence",
        help="Optional human-readable recurrence description.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional extra context for the reminder.",
    ),
) -> None:
    service = bootstrap.build_reminder_service()

    try:
        reminder = service.record(
            title=title,
            cadence=cadence,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Reminder recorded.")
    typer.echo(f"[{reminder.id}] {reminder.title}")


@reminder_app.command("update")
def update(
    reminder_id: int = typer.Argument(
        ...,
        help="The ID of the reminder to update.",
    ),
    cadence: str | None = typer.Option(
        None,
        "--cadence",
        help="Optional updated recurrence description.",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        help="Optional updated extra context for the reminder.",
    ),
) -> None:
    service = bootstrap.build_reminder_service()

    try:
        reminder = service.update(
            reminder_id=reminder_id,
            cadence=cadence,
            details=details,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Reminder updated.")
    typer.echo(f"[{reminder.id}] {reminder.title}")


@reminder_app.command("retire")
def retire(
    reminder_id: int = typer.Argument(
        ...,
        help="The ID of the reminder to retire.",
    ),
    reason: str | None = typer.Option(
        None,
        "--reason",
        help="Optional reason the reminder is no longer active.",
    ),
) -> None:
    service = bootstrap.build_reminder_service()

    try:
        reminder = service.retire(
            reminder_id=reminder_id,
            reason=reason,
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    finally:
        service.repository.session_factory.close()

    typer.echo("Reminder retired.")
    typer.echo(f"[{reminder.id}] {reminder.title}")


@reminder_app.command("list")
def list_reminders(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent reminders to show.",
    ),
) -> None:
    service = bootstrap.build_reminder_service()

    try:
        reminders: list[Reminder] = service.list_recent(limit=limit)
    finally:
        service.repository.session_factory.close()

    if not reminders:
        typer.echo("No reminders found.")
        return

    display_reminders(reminders)