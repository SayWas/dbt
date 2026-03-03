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

## Если скрипт падает на `set -euo pipefail`

Причина: shell-скрипт или compose-файл попал на сервер с Windows-окончаниями (`CRLF`) и/или BOM.
Тогда bash читает строку как `set -euo pipefail\r` и падает с `invalid option name`.

Нормализация на сервере:

```bash
sed -i '1s/^\xEF\xBB\xBF//' infra/scripts/*.sh
sed -i 's/\r$//' infra/scripts/*.sh .env infra/docker-compose.server.yml
```

Проверка синтаксиса:

```bash
bash -n infra/scripts/deploy.sh && echo "deploy.sh syntax OK"
```

Профилактика в репозитории:

- В проекте уже добавлен `.gitattributes` с `eol=lf` для `*.sh`, `*.yml`, `.env*`.
- После изменения этого файла можно один раз сделать `git add --renormalize .` и закоммитить нормализованные файлы.

## Если `dbt deps` падает в Airflow

Частая причина на Linux-сервере: Airflow запускается от uid `50000`, а примонтированный `dwh/` принадлежит другому пользователю. В итоге `dbt deps` не может писать `dbt_packages/` и падает с `exit status 2`.

Решение:

- В `.env` на сервере выставить `AIRFLOW_UID` в uid текущего deploy-пользователя (`id -u`).
- Перезапустить стек через `bash infra/scripts/deploy.sh`.
