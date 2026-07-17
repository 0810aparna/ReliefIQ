# ADR-001: FastAPI over Flask

## Status
Accepted

## Context
ReliefIQ needed a backend framework to expose the prediction, decision,
and optimization pipeline as an API consumed by a separate Streamlit
dashboard. The API needed request/response validation (district IDs,
prediction payloads) and had to be quick to build and test given the
project's timeline.

## Decision
Use FastAPI.

## Alternatives Considered
- **Flask**: more widely known, larger ecosystem of tutorials, but
  requires additional libraries (Marshmallow/Pydantic bolted on
  separately) for request validation, and has no built-in interactive
  API documentation.
- **Django REST Framework**: far more capable but heavyweight for a
  project with no need for Django's ORM, admin panel, or templating —
  would have added setup overhead with no corresponding benefit here.

## Consequences
FastAPI's native Pydantic integration meant request/response schemas
(`database/schemas.py`) doubled as both validation and documentation.
The auto-generated `/docs` page was used directly for manual endpoint
testing throughout development (e.g., verifying `/predict` and
`/optimize` before wiring up the dashboard), which saved having to
write a separate API client just to test the backend. The tradeoff is
a framework with a shorter history than Flask, though this was not a
practical concern for a project of this scope.