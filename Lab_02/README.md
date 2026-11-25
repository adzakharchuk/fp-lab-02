# Лабораторна робота №2 — спортивний рейтинг (варіант 5)

## Мета
Закріпити роботу з функціями вищого порядку, `lambda`, `map`, `filter`, `reduce`, композицією функцій та побудовою функціонального конвеєра без мутації вхідних даних.

## Структура запису
Кожен спортсмен має поля `id: int`, `name: str`, `category: str`, `results: list[float]`. Після обробки додаються `best_result`, `avg_points` і `points`.

## Правило розрахунку
Основним балом рейтингу є середнє арифметичне значень `results`. Найкраще значення зберігається окремо у `best_result`. Для вибраної категорії застосовується множник `factor`. Спортсмен допускається до рейтингу, якщо його скоригований бал не нижчий за `min-points`. Сортування: `points` за спаданням, потім `id` за зростанням. Статистика `reduce_stats` рахується за всіма допущеними спортсменами до обмеження Top-N.

## Встановлення та запуск
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m lab2.main --data lab2/sample_data.json --top 3
```

Приклад із параметрами:
```bash
python -m lab2.main --data lab2/sample_data.json --top 5 --bonus-category Open --factor 1.15 --min-points 80
```

## Перевірки якості
```bash
black --check .
ruff check .
mypy lab2
```

## Структура проєкту
- `lab2/lab2.py` — типи та чисті функції конвеєра;
- `lab2/main.py` — CLI та введення/виведення;
- `lab2/sample_data.json` — демонстраційні дані;
- `lab2/tests/test_lab2.py` — автоматичні тести;
- `pyproject.toml` — конфігурація Black, Ruff і mypy;
- `ASSIGNMENT.md` — формалізовані умови та критерії;
