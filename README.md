# Alfred

Alfred is a self-hostable, local-first household memory and automation project.

Today, Alfred is an early CLI-first foundation for capturing and reviewing durable household memory. It already supports multiple memory domains, not just raw notes, and is being built to grow into a broader household intelligence and orchestration system over time.

Alfred starts small on purpose: establish dependable local persistence, clear architectural boundaries, and testable domain slices first, then expand into richer context, live-state awareness, and bounded automation.

---

## Current status

Alfred is currently an early-stage Python CLI application with local persistence and a growing domain-oriented architecture.

At this stage, Alfred includes implemented support for:

- notes
- people
- decision records
- household facts
- assets
- purchases

This is still foundation work, not the final shape of the system.

---

## Project direction

The long-term goal for Alfred is to become a self-hostable household intelligence and orchestration layer that can help a household:

- remember important long-term knowledge
- model relevant context
- understand selected live state from connected systems
- surface useful advice and procedures
- coordinate bounded practical actions

Home Assistant is expected to become Alfred's primary operational bridge for live home state and automation.

That means Alfred should eventually grow beyond today's capabilities into things like:

- richer person and household context
- decisions and rationale
- asset records
- care instructions
- procedures
- maintenance history
- reminders
- state-aware guidance
- safe orchestration flows

---

## Features today

Current implemented capabilities include:

- capture notes from the command line
- list recent notes
- search notes by text
- register known people
- mark household members
- list people and their household status
- record structured decisions
- list recent decision records
- record household facts
- update household facts
- retire household facts
- list household facts
- record household assets
- list household assets
- record purchases
- list purchases
- store household memory locally in SQLite

---

## Quick start

Clone the repository and install dependencies:

    git clone git@github.com:HHHoegsted/alfred.git
    cd alfred
    uv sync

Run Alfred:

    uv run alfred hello

Work with notes:

    uv run alfred note capture "Remember to buy milk"
    uv run alfred note list
    uv run alfred note search milk

Work with people:

    uv run alfred person add --name "Sara" --household-member
    uv run alfred person list

Work with decisions:

    uv run alfred decision record --summary "Use SQLAlchemy" --reason "Easier later move to Postgres"
    uv run alfred decision list

Work with household facts:

    uv run alfred fact add --subject "Water shutoff valve" --value "Under kitchen sink" --details "Turn clockwise to close"
    uv run alfred fact update 1 --value "Under utility sink" --details "Turn clockwise to close"
    uv run alfred fact retire 1 --reason "No longer correct after renovation"
    uv run alfred fact list

Work with assets:

    uv run alfred asset record "LG Washing Machine" --category "Appliance" --location "Utility room" --brand "LG" --model "F4Y5EYP6J"
    uv run alfred asset list

Work with purchases:

    uv run alfred purchase record "Vacuum bags" --vendor "Power" --purchase-date "2026-03-18T12:00:00" --price-amount "249.95" --currency "DKK" --order-reference "WEB-12345"
    uv run alfred purchase list

Show Alfred's memory-oriented command guidance:

    uv run alfred help-memory

---

## CLI overview

Alfred currently exposes these top-level commands and command groups:

- `hello`
- `help-memory`
- `note`
- `person`
- `decision`
- `fact`
- `asset`
- `purchase`

### Notes

Commands for working with notes:

- `alfred note capture`
- `alfred note list`
- `alfred note search`

### People

Commands for working with known people:

- `alfred person add`
- `alfred person list`

### Decision records

Commands for working with decisions:

- `alfred decision record`
- `alfred decision list`

### Household facts

Commands for working with household facts:

- `alfred fact add`
- `alfred fact update`
- `alfred fact retire`
- `alfred fact list`

### Assets

Commands for working with household assets:

- `alfred asset record`
- `alfred asset list`

### Purchases

Commands for working with purchases:

- `alfred purchase record`
- `alfred purchase list`

---

## Local storage

Alfred uses local persistence and is intended to remain local-first at its core.

At the current stage, Alfred stores data in SQLite on the local machine.

The database file is created automatically in the user's home directory:

    ~/.alfred/alfred.db

The schema is expected to evolve over time as Alfred grows from simple memory capture into richer household memory and context models.

---

## Architecture

Alfred is being developed toward a clean, modular structure with focused files and clear folder boundaries.

Conceptually, the project follows a layered flow like this:

    CLI
    ↓
    Application / Service layer
    ↓
    Repository layer
    ↓
    Persistence layer

Typical responsibilities are:

### CLI

Handles command-line interaction and user-facing commands.

### Application / service layer

Contains use-case logic and orchestration of domain behavior.

### Repository layer

Handles persistence concerns and data access boundaries.

### Persistence / database layer

Owns database setup, sessions, and storage-specific details.

### Domain layer

Represents Alfred's long-term knowledge model, such as notes, people, decision records, household facts, assets, purchases, and related concepts as they are introduced.

---

## Design principles

Alfred is guided by a few core principles:

- **Local-first** — Alfred should remain useful under local control
- **Privacy-first** — household knowledge should not depend on cloud-first assumptions
- **Useful before flashy** — dependable behavior matters more than novelty
- **Non-LLM foundation first** — structured memory and system value come before conversational polish
- **Incremental growth** — build in small, testable slices
- **Modular structure** — prefer focused files and neat folder layouts over monoliths
- **Self-hostable future** — Alfred should eventually be usable by households beyond a single deployment

---

## Development

Run the test suite with:

    uv run pytest

Alfred is intended to grow in a disciplined way so early shortcuts do not become long-term structural problems.

The codebase should continue moving toward:

- clear responsibilities
- modular structure
- replaceable infrastructure
- strong test coverage
- maintainable domain growth

---

## Roadmap

Near- and mid-term directions for Alfred include:

- richer household memory models
- expanded person-context support
- expanded decision memory
- structured records beyond freeform notes
- improved repository and service boundaries
- better export and portability support
- Home Assistant integration
- selected live-state awareness
- reminders, resurfacing, and procedural guidance
- future bounded orchestration flows

The exact order may change, but the direction is consistent: Alfred should grow from local memory foundation into a real household assistant and orchestration platform.

---

## Versioning

Alfred is still in the early `0.x` stage.

That means the project is intentionally evolving quickly while the foundations are still being shaped. Version numbers in this stage represent meaningful progress, but not a stable finished platform.

---

## License

Copyright 2026 Hans-Henrik Høgsted

Licensed under the Apache License, Version 2.0.

See:

- `LICENSE`
- `NOTICE`