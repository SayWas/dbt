# Архитектура проекта

## Сквозная схема (end-to-end)

```text
+-----------------------------------------------------------------------+
|                    External Price Provider                            |
|                         Aviasales API                                 |
+-----------------------------------------------------------------------+
                                   | HTTP/REST
                                   v
+-----------------------------------------------------------------------+
|                    FastAPI Application (app/)                         |
|  - Генерация/получение цен (API + mock fallback)                      |
|  - Нормализация payload                                                |
|  - Запись сырых событий в MongoDB                                     |
+-----------------------------------------------------------------------+
                                   | write raw events
                                   v
+-----------------------------------------------------------------------+
|                     MongoDB (Operational Source)                      |
|  DB: airfares, collection: raw_flight_prices                          |
|  Назначение: оперативное хранение исходных событий                    |
+-----------------------------------------------------------------------+
                                   | EL (Airflow DAG)
                                   v
+-----------------------------------------------------------------------+
|                  Apache Airflow (Orchestration Layer)                 |
|  DAG 1: flight_price_generate_dag   -> генерация данных               |
|  DAG 2: mongo_to_postgres_el_dag    -> MongoDB -> PostgreSQL STG      |
|  DAG 3: dbt_transformations_dag      -> dbt run/test + elementary      |
|  DAG 4: elementary_report_dag        -> HTML report observability      |
+-----------------------------------------------------------------------+
                                   | load/transform
                                   v
+-----------------------------------------------------------------------+
|                    PostgreSQL (Analytical Warehouse)                  |
|  STG schema: stg_raw_flight_prices                                    |
|  ODS schema: ods_flight_price_snapshots                               |
|  DWH schema: dwh_route_price_features                                 |
|  DM schema : dm_route_purchase_recommendations                        |
+-----------------------------------------------------------------------+
                                   | query
                                   v
+-----------------------------------------------------------------------+
|                  Analytics Layer (Notebook/Script)                    |
|  analytics/airfare_insights.ipynb, analytics/airfare_insights.py      |
|  Визуализации и бизнес-рекомендации по времени покупки                |
+-----------------------------------------------------------------------+
```

## Логика по слоям данных

- **Source (MongoDB)**: сырые документы о ценах без агрессивной трансформации.
- **STG (PostgreSQL + dbt source/stg)**: приведение типов, стандартизация кодов маршрутов, расчет базовых атрибутов.
- **ODS (dbt incremental / append)**: исторические снимки цен по ключу маршрута и моменту фиксации.
- **DWH (dbt incremental / delete+insert)**: агрегированные фичи динамики цен (распределения и тренды).
- **DM (dbt mart)**: финальная витрина рекомендаций для аналитики и принятия решения.

## Оркестрация и надежность пайплайна

- **Триггерная цепочка DAG**: каждый этап запускает следующий после успешного завершения.
- **Идемпотентный EL**: high-watermark по `captured_at` + upsert через `ON CONFLICT`.
- **Разделение ответственности**: генерация, загрузка, трансформации и отчет observability вынесены в отдельные DAG.
- **Переиспользуемость в проде**: конфигурация через env-переменные и docker-compose.

## DBT уровень (что показывает инженерную зрелость)

- **Jinja и макросы**: параметризация схем/переменных + макрос `route_key`.
- **Две стратегии инкремента**:
  - ODS: `incremental_strategy='append'`
  - DWH: `incremental_strategy='delete+insert'`
- **Сложная SQL-логика**:
  - CTE-цепочки в каждой модели;
  - оконные функции `lag`, `avg over`, `row_number`.
- **Тестирование качества данных**:
  - dbt-core: `not_null`, `unique`, `relationships`, `accepted_values`;
  - elementary: аномалии объема, свежести, колонок и размерностей.

## Observability, CI/CD и эксплуатация

- **Observability**: `elementary_report_dag` генерирует HTML-отчет качества данных.
- **CI/CD**: workflow с этапами quality -> build -> deploy.
- **Качество кода**: pre-commit (`ruff`, `black`, `yamllint`, `sqlfluff`) и единый стиль.
- **Эксплуатация**: деплой через `infra/scripts/deploy.sh`, подготовленные env-шаблоны и checklist.

## Результат для бизнеса

Витрина `dm.dm_route_purchase_recommendations` дает прикладные рекомендации:

- за сколько дней до вылета покупать билет;
- в какой день недели и час лучше искать билет;
- какие маршруты более волатильны и где выше риск роста цены.
