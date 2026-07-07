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

## Equity Cap (added after observing all-or-nothing allocation in testing)
A linear priority-weighted objective, without an explicit fairness bound,
mathematically prefers concentrating all resources in the single highest-
priority district (equivalent to the fractional knapsack problem). This is
mathematically correct given the stated objective, but operationally
undesirable — real relief distribution should never leave every other
flagged district with zero. Added a hard cap: no district may receive more
than 40% of the total available stock in one allocation round, forcing
the solver to spread across at least 3 districts even under scarcity.

## Note on Scale
total_food_available=5000 in current test runs is an illustrative demo
value, not a calibrated real inventory figure — real Kerala relief
operations would involve stockpiles several orders of magnitude larger.
At this demo scale, only the top 2-3 priority districts receive any
allocation; this is a realistic consequence of genuine scarcity, not a
solver defect. A more realistic total (e.g., in the hundreds of
thousands) would be used for actual deployment scenarios.
