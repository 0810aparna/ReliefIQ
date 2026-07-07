"""
Priority-weighted resource allocation with real constraints: total
inventory, shelter capacity, and transport capacity per district.
"""
import pulp


def optimize_allocation_v2(demands: dict, priorities: dict, shelter_caps: dict,
                            transport_limits: dict, total_food_available: int) -> dict:
    prob = pulp.LpProblem("PriorityWeightedAllocation", pulp.LpMaximize)
    districts = list(demands.keys())

    alloc_vars = {}
    for d in districts:
        upper_bound = min(demands[d], shelter_caps.get(d, demands[d]), transport_limits.get(d, demands[d]))
        alloc_vars[d] = pulp.LpVariable(f"alloc_{d}", lowBound=0, upBound=upper_bound)

    # Objective: maximize priority-weighted allocation (fixes the Phase 1
    # issue where the optimizer arbitrarily gave everything to one district)
    prob += pulp.lpSum(priorities[d] * alloc_vars[d] for d in districts)

    # Constraint: can't exceed total available inventory
    prob += pulp.lpSum(alloc_vars.values()) <= total_food_available

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return {
        "status": pulp.LpStatus[status],
        "allocation": {d: alloc_vars[d].varValue for d in districts},
    }