# Анализ цен на авиабилеты (ETL + DWH + витрина рекомендаций)

Проект реализует полный цикл данных: от генерации/получения цен на авиабилеты до аналитической витрины с рекомендациями, когда выгоднее покупать билет.  
Репозиторий объединяет сервис сбора данных, оркестрацию, хранилище, слой трансформаций dbt и аналитическую визуализацию.

## Что решает проект

Практическая задача - перевести поток сырых ценовых событий в стабильную и понятную модель данных, из которой можно получить прикладные ответы:

- за сколько дней до вылета обычно выгоднее покупать;
- в какой день недели и час лучше искать билеты;
- какие направления более волатильны и где выше риск роста цены.

## Сквозной поток данных

1. FastAPI сервис получает цены (или генерирует fallback-данные) и пишет сырой поток в MongoDB.
2. Airflow запускает EL-загрузку из MongoDB в PostgreSQL (`stg.stg_raw_flight_prices`).
3. dbt строит последующие слои:
   - `ODS` (`ods.ods_flight_price_snapshots`) - исторические снимки цен,
   - `DWH` (`dwh.dwh_route_price_features`) - агрегаты и трендовые признаки,
   - `DM` (`dm.dm_route_purchase_recommendations`) - итоговая витрина рекомендаций.
4. Elementary генерирует отчет наблюдаемости качества данных.
5. Ноутбук и Python-скрипт в `analytics/` визуализируют результаты витрины.

Дополнительное описание архитектурных решений находится в `docs/architecture.md`.

## Состав репозитория

- `app/` - HTTP сервис на FastAPI, запись сырых событий в MongoDB.
- `airflow/` - DAG и jobs для оркестрации `generate -> EL -> dbt -> report`.
- `dwh/` - dbt-проект: модели, макросы, тесты, конфигурация профилей.
- `analytics/` - ноутбук и скрипт визуализации по витрине DM.
- `infra/` - server compose, env-шаблоны, скрипты деплоя и чек-лист.
- `docs/` - архитектурные и эксплуатационные материалы.

## Технологический стек

- Python, FastAPI, Pydantic, httpx
- MongoDB
- PostgreSQL
- Apache Airflow
- dbt-core + dbt-postgres
- elementary-data
- pandas + plotly
- Docker / Docker Compose
- GitHub Actions (CI/CD)

## Быстрый локальный запуск

1. Подготовьте переменные:

   ```bash
   cp .env.example .env
   ```

2. Запустите окружение:

   ```bash
   docker compose up -d --build
   ```

3. Проверьте сервисы:
   - App health: `http://localhost:8000/health`
   - Airflow UI: `http://localhost:8080`
   - MongoDB UI: `http://localhost:8081`

4. В Airflow запустите `flight_price_generate_dag`.  
   Остальные этапы запускаются автоматически по цепочке:
   - `mongo_to_postgres_el_dag`
   - `dbt_transformations_dag`
   - `elementary_report_dag`

5. После успешного прогона проверьте:
   - витрину в PostgreSQL;
   - отчет observability: `http://localhost:8000/reports/elementary`.

## Модель данных и назначение слоев

- **Source (MongoDB)**: `raw_flight_prices`  
  Сырые документы без избыточной бизнес-логики.

- **STG (PostgreSQL)**: `stg.stg_raw_flight_prices`  
  Базовая стандартизация: типы, верхний регистр кодов маршрутов, первичная чистка.

- **ODS**: `ods.ods_flight_price_snapshots`  
  Инкрементальные снимки цен по маршрутам и времени фиксации.

- **DWH**: `dwh.dwh_route_price_features`  
  Агрегаты и признаки динамики: квантили, лаги, скользящие средние.

- **DM**: `dm.dm_route_purchase_recommendations`  
  Бизнес-ориентированная витрина с рекомендациями для выбора времени покупки.

## Как посмотреть итоговую витрину

Подключитесь к PostgreSQL и выполните:

```sql
select
    route_origin,
    route_destination,
    best_days_before_departure,
    best_search_weekday,
    best_search_hour,
    route_avg_price,
    route_price_stddev,
    route_price_cv
from dm.dm_route_purchase_recommendations
order by route_avg_price;
```

Или используйте:

- `analytics/airfare_insights.ipynb` (интерактивный просмотр),
- `analytics/airfare_insights.py` (скриптовый запуск графиков и табличного вывода).

## Оркестрация и эксплуатационные детали

- DAG-цепочка разделена по зонам ответственности: генерация, загрузка, трансформации, отчет.
- EL-процесс идемпотентный: используется high-watermark по `captured_at` и upsert в STG.
- Для деплоя на сервер предназначены:
  - `infra/docker-compose.server.yml`
  - `infra/scripts/deploy.sh`
  - `infra/DEPLOY_CHECKLIST.md`

## Качество кода и данных

- Локальные хуки: `ruff`, `ruff-format`, `black`, `yamllint`, `sqlfluff`.
- В dbt используются CTE и оконные функции для аналитических признаков.
- Модели документированы в `schema.yml`.
- Контроль качества данных сочетает dbt-тесты и elementary-тесты.

## CI/CD

Pipeline в `.github/workflows/ci-cd.yml` выполняет:

- `quality` - линтеры, форматирование, проверка dbt;
- `build` - сборка образов;
- `deploy` - удаленный деплой на сервер при push в `main`.

Правила защищенной ветки и процесс PR описаны в `docs/github_setup.md`.

## Полезные ссылки по проекту

- Архитектура: `docs/architecture.md`
- Шаблон комментария для сдачи: `docs/submission_comment_template.md`
- Пример заполнения: `docs/submission_comment_example.md`
