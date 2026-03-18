import typer

from alfred.bootstrap import (
    build_decision_record_service,
    build_household_fact_service,
    build_note_service,
    build_person_service,
    build_asset_service,
)

from alfred.commands.decisions import decision_app
from alfred.commands.person_context import person_app
from alfred.commands.notes import notes_app
from alfred.commands.fact import fact_app
from alfred.commands.assets import asset_app
from alfred.commands.help_memory import help_memory


app = typer.Typer(help="Alfred is a local-first CLI for capturing and reviewing household memory.")


app.add_typer(decision_app, name="decision")
app.add_typer(person_app, name="person")
app.add_typer(notes_app, name="note")
app.add_typer(fact_app, name="fact")
app.add_typer(asset_app, name="asset")
# single commands
app.command("help-memory")(help_memory)


@app.command()
def hello() -> None:
    typer.echo("Alfred is alive.")


if __name__ == "__main__":
    app()