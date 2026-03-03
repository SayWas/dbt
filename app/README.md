# App: генерация цен на авиабилеты

Python HTTP сервис публикует endpoint для генерации цен и сохраняет результат в MongoDB.

## Endpoints

- `GET /health` — health check.
- `POST /api/v1/prices/generate` — генерация и запись цен в MongoDB.
- `GET /reports/elementary` — HTML дашборд Elementary (EDR report).

## Пример запроса

```json
{
  "origins": ["SVO", "DME"],
  "destinations": ["IST", "LED"],
  "days_ahead": 30
}
```

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```
