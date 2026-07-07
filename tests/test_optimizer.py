import sys
sys.path.append(".")
from optimization.allocator import optimize_allocation_v2


def test_respects_total_inventory():
    result = optimize_allocation_v2(
        demands={1: 1000, 2: 1000}, priorities={1: 0.9, 2: 0.3},
        shelter_caps={1: 2000, 2: 2000}, transport_limits={1: 2000, 2: 2000},
        total_food_available=1000,
    )
    total_allocated = sum(result["allocation"].values())
    assert total_allocated <= 1000 + 1e-6


def test_prefers_higher_priority():
    result = optimize_allocation_v2(
        demands={1: 1000, 2: 1000}, priorities={1: 0.9, 2: 0.1},
        shelter_caps={1: 2000, 2: 2000}, transport_limits={1: 2000, 2: 2000},
        total_food_available=500,
    )
    assert result["allocation"][1] >= result["allocation"][2]


def test_respects_shelter_capacity():
    result = optimize_allocation_v2(
        demands={1: 1000}, priorities={1: 0.9},
        shelter_caps={1: 200}, transport_limits={1: 2000},
        total_food_available=1000,
    )
    assert result["allocation"][1] <= 200 + 1e-6