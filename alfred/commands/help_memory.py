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

fact add
  Store a durable household fact.
  Example:
    alfred fact add --subject "Water shutoff valve" --value "Under kitchen sink" --details "Turn clockwise to close"

fact update
  Update the value or details of a household fact.
  Example:
    alfred fact update 1 --value "Under utility sink" --details "Turn clockwise to close"

fact retire
  Retire a household fact that is no longer active.
  Example:
    alfred fact retire 1 --reason "No longer correct after renovation"

asset record
  Register a household asset.
  Example:
    alfred asset record "LG Washing Machine" --category "Appliance" --location "Utility room"

purchase record
  Store a purchase record.
  Example:
    alfred purchase record "Vacuum bags" --vendor "Power" --purchase-date "2026-03-18T12:00:00" --price-amount "249.95" --currency "DKK"

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

fact list
  Review recorded household facts.
  Example:
    alfred fact list

asset list
  Review recorded household assets.
  Example:
    alfred asset list

purchase list
  Review recorded purchases.
  Example:
    alfred purchase list

remember
  Reserved for future retrieval of durable household knowledge.
  Not implemented yet.
"""
    )