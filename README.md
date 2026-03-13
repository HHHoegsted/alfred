# Alfred

Alfred is a local-first personal assistant CLI for capturing and reviewing notes.

The project starts small on purpose: a simple command-line tool with clean layering and a replaceable storage backend. The long-term goal is to let Alfred grow into a broader personal automation platform without throwing away the early foundation.

---

## Features

- Capture notes from the command line
- Store notes in a local SQLite database
- List recent notes
- Search notes by text
- Validate basic CLI input

---

## Quick start

Clone the repository and install dependencies:

    git clone git@github.com:HHHoegsted/alfred.git
    cd alfred
    uv sync

Run Alfred:

    uv run alfred hello
    uv run alfred capture "Remember to buy milk"
    uv run alfred list
    uv run alfred search milk

---

## Database

Alfred uses SQLite for local storage.

The database file is created automatically in the user's home directory:

    ~/.alfred/alfred.db

Current schema:

- `notes`
  - `id`
  - `timestamp`
  - `text`

An index on `timestamp` is created for faster listing and search result ordering.

---

## Architecture

Alfred uses a simple layered structure:

    CLI
    ↓
    Service
    ↓
    Repository
    ↓
    Database

### CLI

Handles command-line interaction using Typer.

### Service layer

Contains application logic.

### Repository layer

Handles persistence and database access.

### Database layer

Creates SQLite connections and initializes the schema.

---

## Design principles

- **Local-first** — Alfred works without external services
- **Simple CLI first** — start small, automate later
- **Replaceable infrastructure** — storage and backend choices can evolve
- **Incremental growth** — features should be added in small, testable steps

---

## Development

Run the test suite:

    uv run pytest

Current automated coverage includes:

- repository tests
- service tests
- CLI tests

---

## Roadmap

Planned next steps include:

- tagging
- structured capture
- automated digests
- richer search
- database migration support
- future server deployment

---

## License

Copyright 2026 Hans-Henrik Høgsted

Licensed under the Apache License, Version 2.0.

See:

- `LICENSE`
- `NOTICE`
