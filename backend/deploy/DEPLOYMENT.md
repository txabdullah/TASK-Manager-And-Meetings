# Deployment notes

## Compose (full stack)

From `backend`:

```bash
cp deploy/.env.prod.example .env
# Edit .env (SECRET_KEY, ALLOWED_HOSTS, POSTGRES_*, CORS/CSRF if needed)

docker compose -f docker-compose.prod.yml up -d --build
```

Services: `web` (Gunicorn), `db`, `redis`, `celery`, `celery-beat`. `WEB_PORT` defaults to 8000.

Compose sets `DATABASE_URL` from `POSTGRES_*`. Avoid special characters in `POSTGRES_PASSWORD` unless you set a properly encoded `DATABASE_URL` yourself.

## Pull from GHCR (no build on server)

```bash
export GHCR_IMAGE=ghcr.io/<owner>/<repo>/api:latest
docker login ghcr.io -u USER -p TOKEN
docker compose -f docker-compose.prod.yml -f deploy/docker-compose.ghcr.yml pull
docker compose -f docker-compose.prod.yml -f deploy/docker-compose.ghcr.yml up -d --no-build
```

## HTTPS

Put Nginx/Caddy (or a load balancer) in front; forward `X-Forwarded-Proto` / `X-Forwarded-For`. Set `SECURE_*` and cookie flags in `.env` when using HTTPS.

## One-off

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Prod dependencies: `requirements/prod.txt`. Settings: `config.settings.production`.
