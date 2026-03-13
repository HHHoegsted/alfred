# Alfred

Alfred is a local-first personal assistant CLI.

The goal of Alfred is to act as a lightweight personal information capture system that can later grow into a larger automation platform.

The project is intentionally built with a clean architecture so that the storage backend can later be migrated from SQLite to something like PostgreSQL running on a server.

---

## Current features

- Capture notes from the command line
- Store notes in a local SQLite database
- List recent notes
- Search notes by text
- Validate basic CLI input

Example:

uv run alfred capture "Remember to buy milk"  
uv run alfred list
uv run alfred search milk

---

## Project philosophy

Alfred follows a few guiding principles:

- **Local-first** – works without external services
- **Simple CLI first** – automation can come later
- **Replaceable infrastructure** – database and storage layers can change
- **Incremental growth** – features are added gradually

---

## Architecture

The project uses a simple layered structure:

CLI  
↓  
Service  
↓  
Repository  
↓  
Database  

### CLI (`cli.py`)

Handles command-line interaction using Typer.

### Service layer (`services.py`)

Contains application logic.

### Repository layer (`repositories.py`)

Responsible for persistence and database access.

### Database layer (`db.py`)

Creates connections and initializes the SQLite database.

---

## Database

The current storage backend is SQLite.

The database file is created automatically in the user's home directory at:

    ~/.alfred/alfred.db

Current schema:

notes  
- id  
- timestamp  
- text  

An index on `timestamp` is created for faster queries.

---

## Development setup

Clone the repository and install dependencies:

git clone https://github.com/HHHoegsted/alfred.git  
cd alfred  
uv pip install -e .

Run Alfred:

uv run alfred capture "Hello world"  
uv run alfred list

---

## Roadmap

Planned features:

- tagging
- structured capture
- automated digests
- database migration support
- server deployment

---

## License

Copyright 2026 Hans-Henrik Høgsted

This project is licensed under the **Apache License, Version 2.0**.

You may use, modify, and distribute this software under the terms of the license.

See the following files for details:

LICENSE  
NOTICE
