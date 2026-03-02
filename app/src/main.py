from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .aviasales_client import AviasalesClient
from .config import settings
from .mongo_repository import MongoRepository
from .schemas import GeneratePricesRequest

app = FastAPI(title="Airfare Generator Service", version="1.0.0")

mongo_repo = MongoRepository(settings.mongo_uri, settings.mongo_db, settings.mongo_collection)
aviasales_client = AviasalesClient(
    base_url=settings.aviasales_base_url,
    api_token=settings.aviasales_api_token,
    timeout=settings.app_request_timeout,
)


@app.on_event("startup")
async def on_startup() -> None:
    mongo_repo.ensure_indexes()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.get("/reports/elementary")
async def elementary_report() -> FileResponse:
    report_path = Path("/app/docs/elementary_report.html")
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Elementary report is not generated yet.")
    return FileResponse(report_path, media_type="text/html", filename="elementary_report.html")


@app.post("/api/v1/prices/generate")
async def generate_prices(payload: GeneratePricesRequest) -> dict[str, int]:
    origins = payload.origins or [item.strip() for item in settings.default_origins.split(",") if item.strip()]
    destinations = payload.destinations or [item.strip() for item in settings.default_destinations.split(",") if item.strip()]

    records = await aviasales_client.fetch_prices(
        origins=origins,
        destinations=destinations,
        days_ahead=payload.days_ahead or settings.default_days_ahead,
    )
    inserted_count = mongo_repo.save_many(records)

    return {"generated_records": len(records), "inserted_records": inserted_count}
