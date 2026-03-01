# Server deployment

Папка содержит шаблоны для развёртывания проекта на сервере.

## Что внутри

- `docker-compose.server.yml` — серверная версия compose.
- `env/server.env.example` — шаблон переменных окружения.
- `scripts/bootstrap_server.sh` — первичная подготовка сервера.
- `scripts/deploy.sh` — обновление стека при деплое.

## Минимальный сценарий

1. Скопировать репозиторий на сервер.
2. Создать `.env` из `infra/env/server.env.example`.
3. Выполнить `bash infra/scripts/deploy.sh`.

После деплоя Airflow должен быть доступен на серверном хосте/порту.
