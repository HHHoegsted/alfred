import typer

import alfred.bootstrap as bootstrap
from alfred.common import format_timestamp


decision_app = typer.Typer(help="Record and review structured decisions.")


def display_decision_records(records: list) -> None:
    if not records:
        typer.echo("No decision records found.")
        return

    for record in records:
        pretty_timestamp = format_timestamp(record.created_at.isoformat())
        typer.echo(f"[{record.id}] {pretty_timestamp}")
        typer.echo(f"  Summary: {record.summary}")
        typer.echo(f"  Reason:  {record.reason}")
        typer.echo()


@decision_app.command("record")
def record_decision(
    summary: str = typer.Option(
        ...,
        "--summary",
        help="Short statement of what was decided.",
    ),
    reason: str = typer.Option(
        ...,
        "--reason",
        help="Why the decision was made.",
    ),
) -> None:
    service = bootstrap.build_decision_record_service()
    record = service.record(summary=summary, reason=reason)
    typer.echo(f"Decision recorded. [#{record.id}] {record.summary}")


@decision_app.command("list")
def list_decisions(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        help="Maximum number of recent decision records to show.",
    ),
) -> None:
    service = bootstrap.build_decision_record_service()
    records = service.list_recent(limit=limit)
    display_decision_records(records)