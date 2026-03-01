{% set horizon_days = var('recommendation_horizon_days', 45) %}

{{ config(
    materialized='incremental',
    unique_key='feature_key',
    incremental_strategy='delete+insert',
    on_schema_change='sync_all_columns',
    tags=['dwh']
) }}

with base as (
    select
        route_key,
        route_origin,
        route_destination,
        departure_at::date as departure_date,
        captured_at::date as captured_date,
        days_before_departure,
        price
    from {{ ref('ods_flight_price_snapshots') }}
    where days_before_departure between 0 and {{ horizon_days }}
),
daily_agg as (
    select
        route_key,
        route_origin,
        route_destination,
        departure_date,
        captured_date,
        avg(price) as avg_price,
        min(price) as min_price,
        max(price) as max_price,
        percentile_disc(0.25) within group (order by price) as p25_price,
        percentile_disc(0.50) within group (order by price) as p50_price
    from base
    group by 1, 2, 3, 4, 5
),
with_trend as (
    select
        md5(route_key || '-' || departure_date::text || '-' || captured_date::text) as feature_key,
        route_key,
        route_origin,
        route_destination,
        departure_date,
        captured_date,
        avg_price,
        min_price,
        max_price,
        p25_price,
        p50_price,
        -- lag + rolling average provide short-term trend signals for buy timing.
        lag(avg_price) over (partition by route_key, departure_date order by captured_date) as prev_avg_price,
        avg(avg_price) over (
            partition by route_key, departure_date
            order by captured_date
            rows between 6 preceding and current row
        ) as avg_price_7d
    from daily_agg
)
select
    feature_key,
    route_key,
    route_origin,
    route_destination,
    departure_date,
    captured_date,
    avg_price,
    min_price,
    max_price,
    p25_price,
    p50_price,
    prev_avg_price,
    avg_price_7d
from with_trend
{% if is_incremental() %}
where captured_date >= (select coalesce(max(captured_date), '1970-01-01'::date) from {{ this }})
{% endif %}
