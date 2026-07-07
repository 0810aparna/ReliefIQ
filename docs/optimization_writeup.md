# Optimization Writeup

## Objective
Maximize total priority-weighted resource allocation:
sum(priority_score[d] * allocation[d] for d in flagged_districts)

## Decision Variables
allocation[d]: quantity of food packets allocated to district d (continuous, >= 0)

## Constraints
1. allocation[d] <= min(demand[d], shelter_capacity[d], transport_limit[d])
   — can't allocate more than a district needs, can shelter, or can receive
2. sum(allocation[d] for all d) <= total_food_available
   — can't allocate more than exists in inventory

## Why priority weighting (Phase 3 addition)
Phase 1's unweighted objective (maximize total allocated) treated all
districts as interchangeable, so the solver arbitrarily gave 100% of
inventory to a single district — any allocation using the full budget was
equally "optimal" by that objective. Adding priority weights breaks that
tie meaningfully: the solver now prefers allocating to higher-priority
(higher risk, higher population, lower infrastructure) districts first.

## Feasibility
This formulation only has upper-bound constraints on individual
allocations plus one total-inventory constraint — it is always feasible
(the solver can allocate zero everywhere in the extreme case). Hard
minimum-delivery constraints per district were considered but not added,
since introducing them without real operational minimums (e.g., regulatory
delivery guarantees) would be arbitrary — flagged as a natural v2 extension
if such minimums become defined.

## Known Limitations
- shelter_capacity and transport_limit are illustrative conversions from
  infrastructure counts (shelters x 1000, roads x 50), not measured
  logistics data — disclosed as an assumption, not fact.