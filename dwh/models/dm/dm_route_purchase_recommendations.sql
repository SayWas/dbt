{% set min_segment_samples = var('min_segment_samples', 3) %}

{{ config(materialized='table', tags=['dm', 'vitrina']) }}

with base as (
    select
        route_key,
        route_origin,
        route_destination,
        days_before_departure,
        extract(dow from captured_at)::int as search_weekday_num,
        extract(hour from captured_at)::int as search_hour,
        price
    from {{ ref('ods_flight_price_snapshots') }}
    where days_before_departure between 0 and 120
),
route_stats as (
    select
        route_key,
        route_origin,
        route_destination,
        count(*) as samples_total,
        avg(price) as route_avg_price,
        stddev_samp(price) as route_price_stddev,
        min(price) as route_min_price,
        max(price) as route_max_price
    from base
    group by 1, 2, 3
),
lead_time_stats as (
    select
        route_key,
        days_before_departure,
        count(*) as segment_samples,
        avg(price) as avg_price_for_days_before_departure
    from base
    group by 1, 2
),
best_lead_time as (
    select
        route_key,
        days_before_departure as best_days_before_departure,
        avg_price_for_days_before_departure,
        segment_samples,
        row_number() over (
            partition by route_key
            order by avg_price_for_days_before_departure asc, segment_samples desc
        ) as rn
    from lead_time_stats
    where segment_samples >= {{ min_segment_samples }}
),
search_time_stats as (
    select
        route_key,
        search_weekday_num,
        search_hour,
        count(*) as segment_samples,
        avg(price) as avg_price_for_search_slot
    from base
    group by 1, 2, 3
),
best_search_slot as (
    select
        route_key,
        search_weekday_num,
        search_hour as best_search_hour,
        avg_price_for_search_slot,
        segment_samples,
        row_number() over (
            partition by route_key
            order by avg_price_for_search_slot asc, segment_samples desc
        ) as rn
    from search_time_stats
    where segment_samples >= {{ min_segment_samples }}
),
final as (
    select
        route_stats.route_key,
        route_stats.route_origin,
        route_stats.route_destination,
        route_stats.samples_total,
        best_lead_time.best_days_before_departure,
        best_lead_time.avg_price_for_days_before_departure,
        best_search_slot.search_weekday_num,
        best_search_slot.best_search_hour,
        best_search_slot.avg_price_for_search_slot,
        route_stats.route_avg_price,
        route_stats.route_price_stddev,
        case
            when route_stats.route_avg_price = 0 then null
            else route_stats.route_price_stddev / route_stats.route_avg_price
        end as route_price_cv,
        route_stats.route_min_price,
        route_stats.route_max_price
    from route_stats
    left join best_lead_time
        on route_stats.route_key = best_lead_time.route_key
       and best_lead_time.rn = 1
    left join best_search_slot
        on route_stats.route_key = best_search_slot.route_key
       and best_search_slot.rn = 1
)
select
    route_key,
    route_origin,
    route_destination,
    samples_total,
    best_days_before_departure,
    round(avg_price_for_days_before_departure::numeric, 2) as avg_price_for_best_days_before_departure,
    case search_weekday_num
        when 0 then 'Sunday'
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
        else null
    end as best_search_weekday,
    best_search_hour,
    round(avg_price_for_search_slot::numeric, 2) as avg_price_for_best_search_slot,
    round(route_avg_price::numeric, 2) as route_avg_price,
    round(route_price_stddev::numeric, 2) as route_price_stddev,
    round(route_price_cv::numeric, 4) as route_price_cv,
    round(route_min_price::numeric, 2) as route_min_price,
    round(route_max_price::numeric, 2) as route_max_price
from final
