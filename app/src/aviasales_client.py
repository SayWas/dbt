from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

import httpx

from .schemas import FlightPriceRecord


class AviasalesClient:
    """Client that tries API first and falls back to deterministic mock generation."""

    def __init__(self, base_url: str, api_token: str, timeout: int = 15) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout

    async def fetch_prices(
        self,
        origins: list[str],
        destinations: list[str],
        days_ahead: int,
    ) -> list[FlightPriceRecord]:
        if self.api_token and self.api_token != "replace_me":
            api_records = await self._fetch_from_api(origins, destinations, days_ahead)
            if api_records:
                return api_records
        return self._mock_prices(origins, destinations, days_ahead)

    async def _fetch_from_api(
        self,
        origins: list[str],
        destinations: list[str],
        days_ahead: int,
    ) -> list[FlightPriceRecord]:
        records: list[FlightPriceRecord] = []
        headers = {"X-Access-Token": self.api_token}
        captured_at = datetime.now(UTC)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for origin in origins:
                for destination in destinations:
                    if origin == destination:
                        continue
                    for day_idx in range(days_ahead):
                        departure = captured_at + timedelta(days=day_idx + 1)
                        params = {
                            "origin": origin,
                            "destination": destination,
                            "departure_at": departure.date().isoformat(),
                            "currency": "rub",
                        }
                        try:
                            response = await client.get(f"{self.base_url}/prices_for_dates", params=params, headers=headers)
                            response.raise_for_status()
                            payload = response.json()
                            price_value = self._extract_price(payload)
                            if price_value is None:
                                continue
                            records.append(
                                FlightPriceRecord(
                                    route_origin=origin,
                                    route_destination=destination,
                                    departure_at=departure,
                                    captured_at=captured_at,
                                    price=price_value,
                                )
                            )
                        except Exception:
                            # In learning environments API limits are common, so one failed call
                            # should not break the whole batch generation.
                            continue
        return records

    @staticmethod
    def _extract_price(payload: dict) -> float | None:
        data = payload.get("data")
        if isinstance(data, list) and data:
            item = data[0]
            for candidate in ("price", "value", "min_price"):
                if candidate in item and item[candidate] is not None:
                    return float(item[candidate])
        if isinstance(data, dict):
            for candidate in ("price", "value", "min_price"):
                if candidate in data and data[candidate] is not None:
                    return float(data[candidate])
        return None

    @staticmethod
    def _mock_prices(origins: list[str], destinations: list[str], days_ahead: int) -> list[FlightPriceRecord]:
        captured_at = datetime.now(UTC)
        result: list[FlightPriceRecord] = []

        random.seed(captured_at.strftime("%Y-%m-%d"))
        for origin in origins:
            for destination in destinations:
                if origin == destination:
                    continue
                baseline = random.randint(5500, 22000)
                for day_idx in range(days_ahead):
                    departure = captured_at + timedelta(days=day_idx + 1)
                    demand_coef = 1.0 + (0.25 if departure.weekday() in (4, 5, 6) else 0.0)
                    lead_time_coef = max(0.8, 1.25 - day_idx / 120)
                    noise = random.uniform(0.9, 1.1)
                    result.append(
                        FlightPriceRecord(
                            route_origin=origin,
                            route_destination=destination,
                            departure_at=departure,
                            captured_at=captured_at,
                            price=round(baseline * demand_coef * lead_time_coef * noise, 2),
                        )
                    )
        return result
