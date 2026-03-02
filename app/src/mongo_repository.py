from datetime import UTC, datetime

from pymongo import MongoClient
from pymongo.collection import Collection

from .schemas import FlightPriceRecord


class MongoRepository:
    """Repository that stores raw generated flight prices into MongoDB."""

    def __init__(self, uri: str, db_name: str, collection_name: str) -> None:
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection: Collection = self.db[collection_name]

    def ensure_indexes(self) -> None:
        self.collection.create_index(
            [("route_origin", 1), ("route_destination", 1), ("departure_at", 1), ("captured_at", 1)],
            name="ix_route_departure_capture",
        )

    def save_many(self, records: list[FlightPriceRecord]) -> int:
        if not records:
            return 0
        docs = []
        for record in records:
            doc = record.model_dump()
            doc["ingested_at"] = datetime.now(UTC)
            docs.append(doc)
        inserted = self.collection.insert_many(docs, ordered=False)
        return len(inserted.inserted_ids)
