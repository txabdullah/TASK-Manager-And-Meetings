# Deployment

## Docker Compose (recommended)

Build and run from the `backend` directory:

```bash
cd backend
cp deploy/.env.prod.example .env
# Edit .env: set SECRET_KEY, ALLOWED_HOSTS, passwords, CORS/CSRF origins

docker compose -f docker-compose.prod.yml up -d --build
```

Services:

| Service | Role |
|---------|------|
| `web` | Gunicorn on port `WEB_PORT` (default 8000) |
| `db` | PostgreSQL 16 |
| `redis` | Celery broker and results |
| `celery` | Background workers |
| `celery-beat` | Scheduled tasks (deadline reminders) |

The web container runs migrations on startup, then starts Gunicorn.

### Environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret (required in production) |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DATABASE_URL` | PostgreSQL URL (set automatically from `POSTGRES_*` in Compose unless overridden) |
| `CELERY_BROKER_URL` | Redis URL (set to `redis://redis:6379/0` in Compose) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins for browser clients |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins if using session/CSRF from browsers |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS (use behind TLS terminator) |
| `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | Set `True` when serving over HTTPS |

### Reverse proxy (HTTPS)

Put Nginx, Caddy, or a cloud load balancer in front of `web`. Forward `X-Forwarded-Proto` and `X-Forwarded-For`; production settings enable `SECURE_PROXY_SSL_HEADER` for correct scheme detection.

Example Nginx location:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### Managed platforms

- **Railway / Render / Fly.io**: Use their PostgreSQL and Redis add-ons; set `DATABASE_URL` and Redis URLs from the dashboard; run the same `web` and `celery` commands.
- **AWS / GCP**: Run containers on ECS/Cloud Run with RDS and ElastiCache/Memorystore.

### One-off commands

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Production settings module

Set `DJANGO_SETTINGS_MODULE=config.settings.production` (done in Docker and `Dockerfile`).

Install dependencies with `pip install -r requirements/prod.txt` (includes Gunicorn, WhiteNoise, `psycopg`, `dj-database-url`).

Run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
```
