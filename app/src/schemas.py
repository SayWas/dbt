from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GeneratePricesRequest(BaseModel):
    origins: list[str] = Field(default_factory=list)
    destinations: list[str] = Field(default_factory=list)
    days_ahead: int = Field(default=30, ge=1, le=365)


class FlightPriceRecord(BaseModel):
    provider: Literal["aviasales"] = "aviasales"
    route_origin: str
    route_destination: str
    departure_at: datetime
    captured_at: datetime
    ticket_class: Literal["economy", "business"] = "economy"
    currency: str = "RUB"
    price: float
