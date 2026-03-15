import typer


def help_memory() -> None:
    typer.echo(
        """Alfred memory actions

WRITE

note capture
  Store quick raw notes.
  Example:
    alfred note capture "Milk, batteries, printer paper"

decision record
  Store structured durable memory, such as decisions.
  Example:
    alfred decision record --summary "Use SQLAlchemy" --reason "Easier later move to Postgres"

person add
  Register a known person in Alfred's memory.
  Example:
    alfred person add --name "Sara" --household-member

READ

note list
  Review recent captured notes.
  Example:
    alfred note list

note search
  Search captured notes.
  Example:
    alfred note search "printer"

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
"""
    )