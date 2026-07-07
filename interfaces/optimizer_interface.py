"""
Contract for anything that allocates resources across districts. The
orchestrator doesn't know or care whether this is a linear program, a
different solver, or a manual rule.
"""

from typing import Protocol, TypedDict


class AllocationResult(TypedDict):
    status: str
    allocation: dict


class ResourceOptimizer(Protocol):
    def optimize(
        self,
        demands: dict,
        priorities: dict,
        shelter_caps: dict,
        transport_limits: dict,
        total_food_available: int,
    ) -> AllocationResult: ...
