from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
from sqlalchemy import MetaData, Table, create_engine, select


def load_dm() -> pd.DataFrame:
    """Load timing and volatility insights mart from PostgreSQL."""

    user = os.getenv("POSTGRES_USER", "dwh")
    password = os.getenv("POSTGRES_PASSWORD", "dwh")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "dwh")
    dm_schema = os.getenv("DM_SCHEMA", "analytics_dm")
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
    dm_table = Table(
        "dm_route_purchase_recommendations",
        MetaData(),
        autoload_with=engine,
        schema=dm_schema,
    )
    query = select(
        dm_table.c.route_origin,
        dm_table.c.route_destination,
        dm_table.c.best_days_before_departure,
        dm_table.c.best_search_weekday,
        dm_table.c.best_search_hour,
        dm_table.c.route_avg_price,
        dm_table.c.route_price_stddev,
        dm_table.c.route_price_cv,
        dm_table.c.route_min_price,
        dm_table.c.route_max_price,
    )
    return pd.read_sql(query, engine)


def main() -> None:
    df = load_dm()
    if df.empty:
        print("No records in DM. Run pipeline first.")
        return

    route_avg = df.sort_values("route_avg_price")
    fig_avg = px.bar(
        route_avg,
        x="route_origin",
        y="route_avg_price",
        color="route_destination",
        title="Средняя цена по направлениям",
    )
    fig_avg.show()

    fig_days = px.bar(
        df.sort_values("best_days_before_departure"),
        x="route_origin",
        y="best_days_before_departure",
        color="route_destination",
        title="Оптимальный горизонт покупки (дни до вылета)",
    )
    fig_days.show()

    fig_volatility = px.scatter(
        df,
        x="route_avg_price",
        y="route_price_stddev",
        color="route_destination",
        hover_data=["route_origin", "best_search_weekday", "best_search_hour"],
        title="Средняя цена и волатильность маршрута",
    )
    fig_volatility.show()

    print("Рекомендованные окна поиска билетов по маршрутам:")
    print(
        df[
            [
                "route_origin",
                "route_destination",
                "best_days_before_departure",
                "best_search_weekday",
                "best_search_hour",
                "route_avg_price",
                "route_price_stddev",
                "route_price_cv",
            ]
        ].head(30)
    )


if __name__ == "__main__":
    main()
