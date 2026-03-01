# GitHub настройки для CI/CD

## 1) PR workflow

- Включить обязательные Pull Request для `main`.
- Запретить merge при красном workflow.

## 2) Branch protection

- Защитить ветку `main`.
- Запретить прямой push в `main` для разработчиков.
- Разрешить merge только через PR.

## 3) GitHub Secrets

Добавить в репозитории секреты:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PATH`
- `DEPLOY_SSH_PRIVATE_KEY`

## 4) Автодеплой

- В `.github/workflows/ci-cd.yml` деплой запускается только для `push` в `main`.
- Деплой выполняется скриптом `infra/scripts/deploy.sh`.
