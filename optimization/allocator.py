"""
Priority-weighted resource allocation with real constraints: total
inventory, shelter capacity, transport capacity, and an equity cap
per district.
"""
import pulp

MAX_SHARE_PER_DISTRICT = 0.4  # equity policy: no single district gets more
                               # than 40% of total available stock in one round


def optimize_allocation_v2(demands: dict, priorities: dict, shelter_caps: dict,
                            transport_limits: dict, total_food_available: int) -> dict:
    prob = pulp.LpProblem("PriorityWeightedAllocation", pulp.LpMaximize)
    districts = list(demands.keys())

    alloc_vars = {}
    for d in districts:
        equity_cap = MAX_SHARE_PER_DISTRICT * total_food_available
        upper_bound = min(
            demands[d],
            shelter_caps.get(d, demands[d]),
            transport_limits.get(d, demands[d]),
            equity_cap,
        )
        alloc_vars[d] = pulp.LpVariable(f"alloc_{d}", lowBound=0, upBound=upper_bound)

    prob += pulp.lpSum(priorities[d] * alloc_vars[d] for d in districts)
    prob += pulp.lpSum(alloc_vars.values()) <= total_food_available

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return {
        "status": pulp.LpStatus[status],
        "allocation": {d: alloc_vars[d].varValue for d in districts},
    }