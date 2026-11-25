"""Автоматичні тести функцій спортивного рейтингу."""

from copy import deepcopy

import pytest

from lab2.lab2 import (
    Athlete,
    AthleteResult,
    apply_category_bonus,
    build_pipeline,
    build_ranked_pipeline,
    calculate_results,
    compose,
    filter_eligible,
    juxt,
    pipe,
    reduce_stats,
    sort_by_points_desc,
    take,
)


@pytest.fixture
def athletes() -> list[Athlete]:
    return [
        {"id": 3, "name": "anna test", "category": "A", "results": [80, 100]},
        {"id": 1, "name": "bohdan test", "category": "B", "results": [90, 90]},
        {"id": 2, "name": "iryna test", "category": "A", "results": [70, 70]},
        {"id": 4, "name": "petro test", "category": "B", "results": []},
    ]


def test_calculate_results_uses_average_and_preserves_best(
    athletes: list[Athlete],
) -> None:
    calculated = list(calculate_results()(athletes))
    assert calculated[0]["avg_points"] == 90.0
    assert calculated[0]["best_result"] == 100.0
    assert calculated[3]["avg_points"] == 0.0
    assert calculated[3]["best_result"] == 0.0


def test_top_n_and_two_sort_keys(athletes: list[Athlete]) -> None:
    result = build_pipeline(top_n=3, category="A", bonus_factor=1.0)(athletes)
    assert [athlete["id"] for athlete in result] == [1, 3, 2]


def test_sort_tie_breaker_is_id_ascending() -> None:
    records: list[AthleteResult] = [
        {"id": 9, "name": "B", "category": "A", "results": [], "points": 10.0},
        {"id": 2, "name": "A", "category": "A", "results": [], "points": 10.0},
    ]
    assert [item["id"] for item in sort_by_points_desc()(records)] == [2, 9]


def test_no_input_mutation(athletes: list[Athlete]) -> None:
    original = deepcopy(athletes)
    build_pipeline(top_n=2, category="A", bonus_factor=1.2)(athletes)
    assert athletes == original


def test_reduce_stats_returns_required_metrics(athletes: list[Athlete]) -> None:
    ranked = build_ranked_pipeline(category="A", bonus_factor=1.0)(athletes)
    stats = reduce_stats(ranked)
    assert stats == {"count": 4.0, "sum_points": 250.0, "avg_points": 62.5}


def test_reduce_stats_for_empty_input() -> None:
    assert reduce_stats([]) == {"count": 0.0, "sum_points": 0.0, "avg_points": 0.0}


def test_category_bonus_and_eligibility(athletes: list[Athlete]) -> None:
    calculated = calculate_results()(athletes)
    boosted = list(apply_category_bonus("A", 1.1)(calculated))
    assert boosted[0]["points"] == pytest.approx(99.0)
    eligible = list(filter_eligible(80.0)(boosted))
    assert [item["id"] for item in eligible] == [3, 1]


def test_compose_pipe_and_juxt() -> None:
    def double(value: int) -> int:
        return value * 2

    def increment(value: int) -> int:
        return value + 1

    assert compose(double, increment)(3) == 8
    assert pipe(3, increment, double) == 8
    both = juxt(double, increment)
    assert both(3) == (6, 4)


def test_take_zero_and_negative() -> None:
    assert take(0)([1, 2]) == []
    with pytest.raises(ValueError):
        take(-1)
