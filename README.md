# Alfred

Alfred is a local-first personal assistant CLI.

The goal of Alfred is to act as a lightweight personal information capture
system that can later grow into a larger automation platform.

The project is intentionally built with a clean architecture so that the
storage backend can later be migrated from SQLite to something like
PostgreSQL running on a server.

---

## Current features

- Capture notes from the command line
- Store notes in a local SQLite database
- List recent notes

Example:

```bash
uv run alfred capture "Remember to buy milk"
uv run alfred list
