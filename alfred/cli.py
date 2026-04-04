import typer

from alfred.commands.assets import asset_app
from alfred.commands.care_instructions import care_instruction_app
from alfred.commands.decisions import decision_app
from alfred.commands.fact import fact_app
from alfred.commands.help_memory import help_memory
from alfred.commands.maintenance_records import maintenance_record_app
from alfred.commands.notes import notes_app
from alfred.commands.person_context import person_app
from alfred.commands.procedures import procedure_app
from alfred.commands.purchase import purchase_app
from alfred.commands.reminders import reminder_app


app = typer.Typer(
    help="Alfred is a local-first CLI for capturing and reviewing household memory."
)


app.add_typer(asset_app, name="asset")
app.add_typer(care_instruction_app, name="care")
app.add_typer(decision_app, name="decision")
app.add_typer(fact_app, name="fact")
app.add_typer(maintenance_record_app, name="maintenance")
app.add_typer(notes_app, name="note")
app.add_typer(person_app, name="person")
app.add_typer(procedure_app, name="procedure")
app.add_typer(purchase_app, name="purchase")
app.add_typer(reminder_app, name="reminder")
app.command("help-memory")(help_memory)


@app.command()
def hello() -> None:
    typer.echo("Alfred is alive.")


if __name__ == "__main__":
    app()