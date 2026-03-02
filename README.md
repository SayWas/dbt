# Анализ цен на авиабилеты

Монорепозиторий финального проекта курса: Python HTTP сервис генерирует и сохраняет данные о ценах в MongoDB, Airflow переносит данные в PostgreSQL, dbt строит слои `STG -> ODS -> DWH -> DM`, а аналитический слой формирует рекомендации по лучшему времени покупки билетов.

## Компоненты

- `app/` — Python HTTP сервис для генерации и записи цен в MongoDB.
- `airflow/` — DAG и джобы оркестрации по шагам `generate -> EL -> dbt run/test`.
- `dwh/` — dbt-проект с моделями и тестами.
- `infra/` — серверный compose, env-шаблоны и скрипты деплоя.
- `analytics/` — ноутбук/код аналитики и визуализаций.
- `docs/` — архитектура и шаблон артефактов для сдачи.

## Быстрый старт (локально)

1. Скопируйте `.env.example` в `.env` и заполните переменные.
2. Поднимите стек:

   ```bash
   docker compose up -d --build
   ```

3. Проверьте доступность:
   - App health: `http://localhost:8000/health`
   - Airflow UI: `http://localhost:8080`
   - MongoDB UI (mongo-express): `http://localhost:8081`
   - Elementary report (после запуска DAG): `http://localhost:8000/reports/elementary`
4. Запустите DAG `flight_price_generate_dag` в Airflow.
   - Он автоматически триггерит `mongo_to_postgres_el_dag`.
   - EL DAG автоматически триггерит `dbt_transformations_dag`.
   - DBT DAG автоматически триггерит `elementary_report_dag`.
5. Проверьте таблицы в PostgreSQL и dbt-слой витрин.

## Слои данных

- **Source**: коллекция MongoDB `raw_flight_prices`.
- **STG**: таблица PostgreSQL `stg_raw_flight_prices`.
- **ODS**: нормализованный слой `ods_flight_price_snapshots`.
- **DWH**: агрегаты и фичи `dwh_route_price_features`.
- **DM**: витрина рекомендаций `dm_route_purchase_recommendations`.

## Критерии качества и тестирования

- Pre-commit: `ruff`, `black`, `yamllint`, `sqlfluff`.
- dbt-core тесты: `not_null`, `unique`, `relationships`, `accepted_values`.
- elementary-data тесты: все 6 типов (аномалии/свежесть/объёмы).

## CI/CD (GitHub Actions)

Workflow в `.github/workflows/ci-cd.yml` включает:

- `quality` — линтеры и форматирование.
- `build` — сборка контейнеров.
- `deploy` — автоматический деплой на сервер при push в `main`.

Подробности по настройке защищённой ветки и PR-процесса в `docs/github_setup.md`.

## Артефакты сдачи

Шаблон единого комментария для сдачи находится в `docs/submission_comment_template.md`.
URL локального elementary-дашборда: `http://localhost:8000/reports/elementary`.
