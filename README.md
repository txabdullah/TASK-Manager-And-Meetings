# AI Meeting Notes & Task Manager API

Django REST API for teams: meeting notes/recordings, AI-style task extraction, assignments, deadlines, and notifications.

**Live API:** http://13.48.12.157:8000/ — interactive docs: `/api/docs/`, `/api/redoc/`.

## Features

- **Auth**: JWT (register, login, logout, password reset; roles)
- **Teams**: create, invite, roles
- **Meetings**: notes and recordings
- **Tasks**: assign, comments, deadlines; background extraction and reminders (Celery + Redis)
- **Docs**: Swagger / ReDoc

## Local dev

**Needs:** Python 3.10+, Redis (Docker is fine).

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements/base.txt
cp .env.example .env
```

Run Redis: `cd backend && docker compose up -d redis` (see `backend/docker-compose.yml`).

```bash
python manage.py migrate
python manage.py runserver
```

Separate terminals: `celery -A config worker -l info` and `celery -A config beat -l info`.

API docs: `http://localhost:8000/api/docs/` and `/api/redoc/`.

Main env vars are in `backend/.env.example` (`SECRET_KEY`, `CELERY_*`, etc.).

## Docker (production-style)

From `backend`, copy `deploy/.env.prod.example` → `.env`, set secrets and hosts, then:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Stack: Postgres, Redis, Gunicorn, Celery, Celery Beat. Migrations run when `web` starts.

GHCR override (pull image instead of build): use `deploy/docker-compose.ghcr.yml` as in [backend/deploy/DEPLOYMENT.md](backend/deploy/DEPLOYMENT.md).

## CI/CD

| Workflow | What it does |
|----------|----------------|
| `ci.yml` | On push/PR to `main` or `master`: tests, then builds the Docker image (no push). |
| `docker-publish.yml` | Pushes `ghcr.io/<owner>/<repo>/api` on default branch, `v*` tags, or manual run. |
| `deploy-aws.yml` | SSH to your server, `docker login` GHCR, pull, `docker compose up`. Manual or after publish. Optional **production** environment for approvals. |

**AWS deploy secrets** (repo → Settings → Secrets and variables → Actions):

| Secret | Value |
|--------|--------|
| `AWS_DEPLOY_HOST` | EC2 **public** IPv4 |
| `AWS_DEPLOY_USER` | e.g. `ubuntu` |
| `AWS_DEPLOY_SSH_KEY` | Full private key PEM |
| `AWS_DEPLOY_PATH` | Path on server with `docker-compose.prod.yml`, `deploy/docker-compose.ghcr.yml`, `.env` |
| `GHCR_USERNAME` | GitHub username |
| `GHCR_READ_TOKEN` | PAT with `read:packages` |

Instance SG must allow SSH (22) from where you connect; GitHub Actions needs reachability on 22 (often `0.0.0.0/0` for small setups).

## Project layout

```
backend/
├── apps/          # users, teams, meetings, tasks, notifications
├── config/
├── deploy/        # prod env example, compose overrides, deployment notes
└── requirements/
```

## License

MIT
