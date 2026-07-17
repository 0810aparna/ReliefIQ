# ADR-002: PostgreSQL over SQLite

## Status
Accepted

## Context
The project needed a relational database for districts, infrastructure,
disaster history, and runtime-logged predictions/decisions/allocations.
Local development and eventual cloud deployment both needed to be
supported.

## Decision
Use PostgreSQL, run via Docker locally and Supabase in production.

## Alternatives Considered
- **SQLite**: zero setup, file-based, would have been sufficient for
  the read-heavy local development workload alone. Rejected because
  (a) it does not support concurrent writes well, which matters once
  the API is logging predictions/decisions on every request, and
  (b) it would not have matched the production deployment target,
  meaning local testing would not have caught connection-string,
  pooling, or concurrency issues that only appear against a real
  Postgres instance — issues that, in practice, did surface during
  cloud deployment (connection string encoding, pooler region
  mismatches) and were easier to debug having already worked with
  Postgres locally via Docker.

## Consequences
Running Postgres locally via Docker Compose from early in the project
meant the schema, Alembic migrations, and SQLAlchemy models were all
validated against the same database engine used in production,
avoiding a class of "works locally, breaks in prod" bugs. The cost was
additional local setup (Docker, connection strings, migrations) versus
SQLite's zero-config file, which was a deliberate tradeoff in favor of
production parity.