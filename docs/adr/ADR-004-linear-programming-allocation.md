# ADR-004: Linear Programming for Resource Allocation

## Status
Accepted

## Context
Once multiple districts are flagged as needing resources, total
available inventory is often less than total demand — the system needs
a principled way to decide the distribution, not a naive equal split
or a purely manual rule.

## Decision
Use linear programming (PuLP) to maximize priority-weighted resource
allocation, subject to inventory, shelter capacity, transport capacity,
and an equity cap (added after testing — see below).

## Alternatives Considered
- **Proportional split by demand**: simple, but ignores
  priority/urgency differences between districts (a high-priority,
  low-population district and a low-priority, high-population district
  would be treated identically per unit of demand).
- **Manual/heuristic rules**: harder to justify as optimal, harder to
  extend with new constraints (shelter capacity, transport limits)
  without the logic becoming an unmanageable nest of conditionals.

## Consequences
Linear programming guarantees a mathematically optimal allocation given
the stated objective and constraints. During testing, an early version
with only priority-weighted objective and no fairness constraint
produced a winner-take-all allocation (100% of stock to the single
highest-priority district) — a mathematically correct but operationally
undesirable outcome, since a linear objective always prefers
concentrating resources in the best-per-unit option (equivalent to the
fractional knapsack problem). This led to adding an explicit equity cap
(no district may receive more than 40% of total available stock in one
round), which is documented as a deliberate policy constraint, not a
solver limitation, in docs/optimization_writeup.md.