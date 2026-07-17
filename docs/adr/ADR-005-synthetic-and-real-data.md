# ADR-005: Historical + Synthetic Data Instead of Only Historical

## Status
Accepted

## Context
Granular, multi-year, district-level flood, weather, and infrastructure
records are not available in one consolidated public source for Kerala
at the scope needed for this project.

## Decision
Use real data where available — district geography and population
(Census India), real 2018 flood event data (Kaggle: Kerala Floods 2018,
including real rainfall in mm, landslide counts, and damage figures),
and real historical rainfall (Kaggle: Rainfall in India, 1901-2015) —
and generate synthetic data only for infrastructure counts (hospitals,
shelters, roads), the one field with no accessible public source at
district granularity, using a documented, population-scaled formula
rather than presenting it as collected fact.

## Alternatives Considered
- Scope down to only fully-real data for every field: would have left
  infrastructure capacity entirely unmodeled, removing a meaningful
  input to the priority-ranking and shelter-capacity constraints.
- Present synthetic data without disclosure: rejected outright —
  undermines the credibility of the whole project if discovered, and
  is a bad practice regardless of discovery risk.

## Consequences
The final dataset is real for districts, population, geography, flood
events, and rainfall — with only infrastructure synthetic and clearly
disclosed in data/DATA_SOURCES.md. This is a stronger, more defensible
position than either an all-synthetic dataset or an unrealistically
narrow all-real dataset would have been.