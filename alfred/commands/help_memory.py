import typer


def help_memory() -> None:
    typer.echo(
        """Alfred memory actions

WRITE

capture
  Store quick raw notes.
  Example:
    alfred capture "Milk, batteries, printer paper"

record
  Store structured durable memory, such as decisions.
  Example:
    alfred decision record --summary "Use SQLAlchemy" --reason "Easier later move to Postgres"

person add
  Register a known person in Alfred's memory.
  Example:
    alfred person add --name "Sara" --household-member

READ

search
  Search captured notes.
  Example:
    alfred search "printer"

decision list
  Review recorded decisions.
  Example:
    alfred decision list

person list
  Review known people Alfred has recorded.
  Example:
    alfred person list

remember
  Reserved for future retrieval of durable household knowledge.
  Not implemented yet.

AVOID

save
  Too generic for Alfred's memory language.
  Prefer capture or record.

LATER

don't forget
  Better suited for reminders/tasks than memory records.
  Not implemented yet.
"""
    )