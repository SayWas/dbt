from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime

import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient


def _mongo_uri() -> str:
    user = os.getenv("MONGO_USER", "root")
    password = os.getenv("MONGO_PASSWORD", "root")
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    auth_db = os.getenv("MONGO_AUTH_DB", "admin")
    return f"mongodb://{user}:{password}@{host}:{port}/?authSource={auth_db}"


def _postgres_dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'postgres')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'dwh')} "
        f"user={os.getenv('POSTGRES_USER', 'dwh')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'dwh')}"
    )


def _record_hash(origin: str, destination: str, departure_at: datetime, captured_at: datetime) -> str:
    value = f"{origin}|{destination}|{departure_at.isoformat()}|{captured_at.isoformat()}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_el_mongo_to_postgres() -> int:
    """Transfer raw airfare records from MongoDB to PostgreSQL STG."""

    mongo_db = os.getenv("MONGO_DB", "airfares")
    mongo_collection = os.getenv("MONGO_COLLECTION", "raw_flight_prices")
    stg_schema = os.getenv("POSTGRES_STG_SCHEMA", "stg")
    stg_table = "stg_raw_flight_prices"

    mongo_client = MongoClient(_mongo_uri())
    collection = mongo_client[mongo_db][mongo_collection]

    with psycopg2.connect(_postgres_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {stg_schema};")
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {stg_schema}.{stg_table} (
                    record_hash TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    route_origin TEXT NOT NULL,
                    route_destination TEXT NOT NULL,
                    departure_at TIMESTAMPTZ NOT NULL,
                    captured_at TIMESTAMPTZ NOT NULL,
                    ticket_class TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    price NUMERIC(12,2) NOT NULL,
                    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )

            # High-watermark load keeps EL idempotent across regular schedules.
            cur.execute(f"SELECT COALESCE(MAX(captured_at), '1970-01-01'::timestamptz) FROM {stg_schema}.{stg_table};")
            (max_captured_at,) = cur.fetchone()

            mongo_filter = {"captured_at": {"$gt": max_captured_at}}
            mongo_docs = list(collection.find(mongo_filter))
            if not mongo_docs:
                return 0

            rows = []
            for doc in mongo_docs:
                departure_at = doc.get("departure_at")
                captured_at = doc.get("captured_at")
                if not departure_at or not captured_at:
                    continue
                route_origin = str(doc.get("route_origin", "")).upper()
                route_destination = str(doc.get("route_destination", "")).upper()
                rows.append(
                    (
                        _record_hash(route_origin, route_destination, departure_at, captured_at),
                        doc.get("provider", "aviasales"),
                        route_origin,
                        route_destination,
                        departure_at,
                        captured_at,
                        doc.get("ticket_class", "economy"),
                        doc.get("currency", "RUB"),
                        float(doc.get("price", 0)),
                        doc.get("ingested_at", datetime.now(UTC)),
                    )
                )

            if not rows:
                return 0

            insert_sql = f"""
                INSERT INTO {stg_schema}.{stg_table} (
                    record_hash,
                    provider,
                    route_origin,
                    route_destination,
                    departure_at,
                    captured_at,
                    ticket_class,
                    currency,
                    price,
                    ingested_at
                ) VALUES %s
                ON CONFLICT (record_hash) DO UPDATE SET
                    price = EXCLUDED.price,
                    ingested_at = EXCLUDED.ingested_at
            """
            execute_values(cur, insert_sql, rows, page_size=200)
        conn.commit()

    return len(rows)
