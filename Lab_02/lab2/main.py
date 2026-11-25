"""CLI-демонстрація спортивного рейтингу; тут зосереджено файловий I/O."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from lab2.lab2 import (
    Athlete,
    build_pipeline,
    build_ranked_pipeline,
    reduce_stats,
)


def load_athletes(path: Path) -> list[Athlete]:
    """Зчитує та базово перевіряє JSON-файл зі спортсменами."""

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Кореневий елемент JSON має бути списком.")
    for index, athlete in enumerate(payload):
        if not isinstance(athlete, dict):
            raise ValueError(f"Запис №{index + 1} має бути JSON-об'єктом.")
        required = {"id", "name", "category", "results"}
        if not required.issubset(athlete):
            raise ValueError(f"У записі №{index + 1} відсутні обов'язкові поля.")
        if not isinstance(athlete["results"], list):
            raise ValueError(f"Поле results у записі №{index + 1} має бути списком.")
        if not all(isinstance(score, (int, float)) for score in athlete["results"]):
            raise ValueError(f"У results запису №{index + 1} є нечислове значення.")
    return cast(list[Athlete], payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Формування спортивного рейтингу")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("lab2/sample_data.json"),
        help="Шлях до JSON-файлу зі спортсменами",
    )
    parser.add_argument("--top", type=int, default=3, help="Кількість позицій Top-N")
    parser.add_argument(
        "--bonus-category", default="Open", help="Категорія, що отримує бонус"
    )
    parser.add_argument(
        "--factor", type=float, default=1.1, help="Коефіцієнт бонусу категорії"
    )
    parser.add_argument(
        "--min-points",
        type=float,
        default=0.0,
        help="Мінімальний бал для допуску до рейтингу",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.top < 0:
        raise SystemExit("Помилка: --top не може бути від'ємним.")
    athletes = load_athletes(args.data)
    ranked = build_ranked_pipeline(args.bonus_category, args.factor, args.min_points)(
        athletes
    )
    top = build_pipeline(args.top, args.bonus_category, args.factor, args.min_points)(
        athletes
    )

    print("СПОРТИВНИЙ РЕЙТИНГ")
    print(
        f"Категорія з бонусом: {args.bonus_category}; "
        f"коефіцієнт: {args.factor}; мінімум: {args.min_points}"
    )
    print(f"\nТОП-{args.top}")
    if not top:
        print("Немає спортсменів, які відповідають умовам.")
    for position, athlete in enumerate(top, start=1):
        print(
            f"{position}. {athlete['name']} | {athlete['category']} | "
            f"бали: {athlete.get('points', 0.0):.2f} | "
            f"найкращий результат: {athlete.get('best_result', 0.0):.2f}"
        )

    stats = reduce_stats(ranked)
    print("\nАГРЕГАЦІЯ ДЛЯ ВСІХ ДОПУЩЕНИХ СПОРТСМЕНІВ")
    print(f"count: {stats['count']:.0f}")
    print(f"sum_points: {stats['sum_points']:.2f}")
    print(f"avg_points: {stats['avg_points']:.2f}")


if __name__ == "__main__":
    main()
