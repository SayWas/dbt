# Deploy checklist

1. Copy `infra/env/server.env.example` to `.env` in project root.
2. Run:

   ```bash
   bash infra/scripts/deploy.sh
   ```

   `deploy.sh` automatically synchronizes `AIRFLOW_UID` in `.env` with the current server user uid.

3. Verify endpoints:
   - `http://185.43.6.198:8000/health`
   - `http://185.43.6.198:8081` (MongoDB UI, mongo-express)
   - `http://185.43.6.198:8000/reports/elementary` (after first successful report run)
   - `http://185.43.6.198:8080` (Airflow)
4. In Airflow, confirm DAGs are enabled:
   - `flight_price_generate_dag`
   - `mongo_to_postgres_el_dag`
   - `dbt_transformations_dag`
   - `elementary_report_dag`
5. Trigger `flight_price_generate_dag` manually once and verify:
   - MongoDB has records in `raw_flight_prices`
   - PostgreSQL has data in `stg/ods/dwh/dm` schemas
6. Save URLs and credentials into `docs/submission_comment_template.md`.
