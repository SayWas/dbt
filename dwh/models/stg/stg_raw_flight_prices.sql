{% set source_schema = env_var('POSTGRES_STG_SCHEMA', 'stg') %}

with source_data as (
    select
        record_hash,
        upper(route_origin) as route_origin,
        upper(route_destination) as route_destination,
        departure_at,
        captured_at,
        ticket_class,
        upper(currency) as currency,
        price::numeric(12, 2) as price,
        ingested_at
    from {{ source(source_schema, 'stg_raw_flight_prices') }}
),
enriched as (
    select
        record_hash,
        route_origin,
        route_destination,
        departure_at,
        captured_at,
        ticket_class,
        currency,
        price,
        ingested_at,
        (departure_at::date - captured_at::date) as days_before_departure,
        extract(dow from departure_at) as departure_day_of_week
    from source_data
)
select * from enriched
