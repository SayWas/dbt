Swagger URL: http://<server-ip>:8000/docs
MongoDB URL: mongodb://<user>:<password>@<server-ip>:27017/?authSource=admin
MongoDB UI URL: http://<server-ip>:8081
PostgreSQL URL: postgresql://<user>:<password>@<server-ip>:5432/dwh
Airflow:
  URL: http://<server-ip>:8080
  User: <airflow_user>
  Password: <airflow_password>
Elementary edr report URL: <edr_report_url>
Презентация URL: <presentation_url>

Витрины для проверки:
- STG: `stg.stg_raw_flight_prices`
- ODS: `ods.ods_flight_price_snapshots`
- DWH: `dwh.dwh_route_price_features`
- DM: `dm.dm_route_purchase_recommendations`
