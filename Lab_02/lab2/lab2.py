"""Чисті функції для побудови спортивного рейтингу без мутації записів."""

from __future__ import annotations

from functools import reduce
from itertools import islice
from typing import Any, Callable, Iterable, Iterator, TypedDict, TypeVar, cast


class Athlete(TypedDict):
    """Вхідний запис спортсмена."""

    id: int
    name: str
    category: str
    results: list[float]


class AthleteResult(Athlete, total=False):
    """Запис спортсмена з розрахованими показниками."""

    best_result: float
    avg_points: float
    points: float


T = TypeVar("T")
R = TypeVar("R")


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Композиція: compose(f, g)(x) еквівалентно f(g(x))."""

    def composed(value: Any) -> Any:
        for function in reversed(functions):
            value = function(value)
        return value

    return composed


def pipe(value: T, *functions: Callable[[Any], Any]) -> Any:
    """Послідовно передає значення через набір функцій зліва направо."""

    return reduce(lambda current, function: function(current), functions, value)


def juxt(*functions: Callable[[T], R]) -> Callable[[T], tuple[R, ...]]:
    """Повертає функцію, яка застосовує всі функції до одного аргументу."""

    return lambda value: tuple(function(value) for function in functions)


def normalize_names() -> Callable[[Iterable[Athlete]], Iterator[Athlete]]:
    """Створює трансформацію нормалізації імен у формат Title Case."""

    return lambda athletes: map(
        lambda athlete: cast(
            Athlete,
            {
                **athlete,
                "name": athlete["name"].strip().title(),
            },
        ),
        athletes,
    )


def calculate_results() -> Callable[[Iterable[Athlete]], Iterator[AthleteResult]]:
    """Додає найкращий результат і середній бал спортсмена."""

    def transform(athletes: Iterable[Athlete]) -> Iterator[AthleteResult]:
        def calculate(athlete: Athlete) -> AthleteResult:
            results = athlete["results"]
            best = max(results, default=0.0)
            average = sum(results) / len(results) if results else 0.0
            return cast(
                AthleteResult,
                {
                    **athlete,
                    "best_result": float(best),
                    "avg_points": float(average),
                    "points": float(average),
                },
            )

        return map(calculate, athletes)

    return transform


def apply_category_bonus(
    category: str, factor: float
) -> Callable[[Iterable[AthleteResult]], Iterator[AthleteResult]]:
    """Множить рейтингові бали на коефіцієнт для заданої категорії."""

    def transform(
        athletes: Iterable[AthleteResult],
    ) -> Iterator[AthleteResult]:
        return map(
            lambda athlete: cast(
                AthleteResult,
                {
                    **athlete,
                    "points": (
                        athlete.get("points", 0.0) * factor
                        if athlete["category"] == category
                        else athlete.get("points", 0.0)
                    ),
                },
            ),
            athletes,
        )

    return transform


def filter_eligible(
    min_points: float,
) -> Callable[[Iterable[AthleteResult]], Iterator[AthleteResult]]:
    """Залишає спортсменів, які набрали не менше мінімального порога."""

    return lambda athletes: filter(
        lambda athlete: athlete.get("points", 0.0) >= min_points,
        athletes,
    )


def sort_by_points_desc() -> Callable[[Iterable[AthleteResult]], list[AthleteResult]]:
    """Сортує за балами спадно, а за однакових балів — за id зростанням."""

    return lambda athletes: sorted(
        athletes,
        key=lambda athlete: (-athlete.get("points", 0.0), athlete["id"]),
    )


def take(n: int) -> Callable[[Iterable[T]], list[T]]:
    """Повертає не більше n перших записів."""

    if n < 0:
        raise ValueError("Параметр Top-N не може бути від'ємним.")
    return lambda athletes: list(islice(athletes, n))


def build_ranked_pipeline(
    category: str = "Open",
    bonus_factor: float = 1.1,
    min_points: float = 0.0,
) -> Callable[[Iterable[Athlete]], list[AthleteResult]]:
    """Будує повний рейтинг усіх допущених спортсменів."""

    if bonus_factor < 0:
        raise ValueError("Коефіцієнт бонусу не може бути від'ємним.")

    return compose(
        sort_by_points_desc(),
        filter_eligible(min_points),
        apply_category_bonus(category, bonus_factor),
        calculate_results(),
        normalize_names(),
    )


def build_pipeline(
    top_n: int = 3,
    category: str = "Open",
    bonus_factor: float = 1.1,
    min_points: float = 0.0,
) -> Callable[[Iterable[Athlete]], list[AthleteResult]]:
    """Будує конвеєр обробки та формування Top-N рейтингу."""

    ranked_pipeline = build_ranked_pipeline(category, bonus_factor, min_points)
    return compose(take(top_n), ranked_pipeline)


def reduce_stats(athletes: Iterable[AthleteResult]) -> dict[str, float]:
    """Обчислює count, sum_points та avg_points за допомогою reduce."""

    initial = {"count": 0.0, "sum_points": 0.0}
    accumulated = reduce(
        lambda acc, athlete: {
            "count": acc["count"] + 1.0,
            "sum_points": acc["sum_points"] + athlete.get("points", 0.0),
        },
        athletes,
        initial,
    )
    count = accumulated["count"]
    total = accumulated["sum_points"]
    average = total / count if count else 0.0
    return {"count": count, "sum_points": total, "avg_points": average}


# Назва Record залишена як узагальнений тип запису з формулювання методички.
Record = Athlete
