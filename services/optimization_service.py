"""
Implements ResourceOptimizer by wrapping the PuLP linear program.
"""

from optimization.allocator import optimize_allocation_v2


class LPOptimizer:
    def optimize(
        self,
        demands: dict,
        priorities: dict,
        shelter_caps: dict,
        transport_limits: dict,
        total_food_available: int,
    ) -> dict:
        return optimize_allocation_v2(
            demands, priorities, shelter_caps, transport_limits, total_food_available
        )
