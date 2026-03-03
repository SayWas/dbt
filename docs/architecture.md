# Архитектура проекта

## Поток данных

1. Python сервис генерирует/запрашивает цены и пишет документы в MongoDB.
2. Airflow запускает цепочку DAG:
   - `flight_price_generate_dag` (генерация/запись в MongoDB),
   - `mongo_to_postgres_el_dag` (перенос в PostgreSQL STG),
   - `dbt_transformations_dag` (dbt run/test + elementary models),
   - `elementary_report_dag` (генерация HTML отчёта observability).
3. dbt строит модели:
   - `stg_raw_flight_prices`
   - `ods_flight_price_snapshots`
   - `dwh_route_price_features`
   - `dm_route_purchase_recommendations`
4. Elementary тесты мониторят аномалии и свежесть.
5. Ноутбук в `analytics/` визуализирует тренды и рекомендации.

## Ключевые решения

- Монорепозиторий для прозрачного CI/CD и единых версий.
- Инкрементальная загрузка в ODS и DWH разными стратегиями.
- Оконные функции для поведенческих сигналов о времени покупки.
