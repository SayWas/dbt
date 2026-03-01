{% set currency = var('default_currency', 'RUB') %}

{{ config(
    materialized='incremental',
    unique_key='record_hash',
    incremental_strategy='append',
    on_schema_change='sync_all_columns',
    tags=['ods']
) }}

with stg as (
    select
        record_hash,
        {{ route_key('route_origin', 'route_destination') }} as route_key,
        route_origin,
        route_destination,
        departure_at,
        captured_at,
        days_before_departure,
        departure_day_of_week,
        ticket_class,
        currency,
        price
    from {{ ref('stg_raw_flight_prices') }}
    where currency = '{{ currency }}'
    {% if is_incremental() %}
      and captured_at > (select coalesce(max(captured_at), '1970-01-01'::timestamp) from {{ this }})
    {% endif %}
)
select
    record_hash,
    route_key,
    route_origin,
    route_destination,
    departure_at,
    captured_at,
    days_before_departure,
    departure_day_of_week,
    ticket_class,
    currency,
    price
from stg
