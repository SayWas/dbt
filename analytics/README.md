# Analytics

Папка содержит артефакты анализа для защиты проекта:

- `airfare_insights.ipynb` — ноутбук с графиками и рекомендациями по времени покупки.
- `airfare_insights.py` — скрипт-версия анализа для запуска без Jupyter.

## Что анализируем

- Среднюю цену по направлениям.
- Динамику цены в зависимости от `days_before_departure`.
- Волатильность маршрутов и оптимальные окна поиска (`best_days_before_departure`, `best_search_weekday`, `best_search_hour`).
