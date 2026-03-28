# AI Meeting Notes & Task Manager API

A Django REST Framework backend for teams to upload meeting recordings/notes, extract tasks automatically, assign them to members, and track progress.

## Features

- **Authentication**: JWT (register, login, logout, password reset, roles: admin/member)
- **Teams**: Create teams, invite members, role-based permissions
- **Meetings**: Upload meeting notes and recordings
- **AI Task Extraction**: Simulated parsing extracts tasks from notes (e.g., "Ali will prepare the budget")
- **Tasks**: Create, assign, update status, add comments, set deadlines
- **Background Processing**: Celery + Redis for async task extraction and reminders
- **Notifications**: Task assigned, deadline approaching, new comment
- **API Documentation**: Swagger UI and ReDoc

## Quick Start

### Prerequisites

- Python 3.10+
- Redis (for Celery)

### Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
cp .env.example .env
```

### Environment Variables

Create a `.env` file (see `backend/.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required in production) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL for results | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | Optional OpenAI for extraction | (empty) |
| `DEFAULT_FROM_EMAIL` | Email sender for password reset | `noreply@example.com` |

### Run Redis (Docker)

```bash
cd backend && docker-compose up -d redis
```

### Migrations

```bash
python manage.py migrate
```

### Run the Server

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery Beat (scheduled reminders)
celery -A config beat -l info
```

### API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Overview

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login (returns access + refresh tokens) |
| POST | `/api/auth/logout/` | Logout (blacklist refresh token) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/password/reset/` | Request password reset |
| POST | `/api/auth/password/reset/confirm/` | Confirm password reset |

### Teams

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/teams/` | List user's teams |
| POST | `/api/teams/` | Create team |
| GET | `/api/teams/{id}/` | Team detail |
| PATCH | `/api/teams/{id}/` | Update team |
| DELETE | `/api/teams/{id}/` | Delete team |
| POST | `/api/teams/{id}/invite/` | Invite member by email |
| GET | `/api/teams/{id}/members/` | List members |
| DELETE | `/api/teams/{id}/members/{user_id}/` | Remove member |

### Meetings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/meetings/` | List meetings |
| POST | `/api/meetings/` | Create meeting |
| GET | `/api/meetings/{id}/` | Meeting detail |
| DELETE | `/api/meetings/{id}/` | Delete meeting |
| POST | `/api/meetings/{id}/notes/` | Add notes (triggers task extraction) |
| POST | `/api/meetings/{id}/recordings/` | Upload recording |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List tasks (filter: team, assignee, status) |
| POST | `/api/tasks/` | Create task |
| GET | `/api/tasks/{id}/` | Task detail |
| PATCH | `/api/tasks/{id}/` | Update task |
| DELETE | `/api/tasks/{id}/` | Delete task |
| POST | `/api/tasks/{id}/assign/` | Assign users |
| GET | `/api/tasks/{id}/comments/` | List comments |
| POST | `/api/tasks/{id}/comments/` | Add comment |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | List notifications |
| PATCH | `/api/notifications/{id}/read/` | Mark as read |
| POST | `/api/notifications/mark-all-read/` | Mark all read |

## Task Extraction

When notes are uploaded, the system parses patterns like:

- `Ali will prepare the budget.` → Task assigned to Ali
- `Sara will contact the supplier.` → Task assigned to Sara
- `Assign to John: Review the report` → Task assigned to John

Names are matched to team members by first name, last name, or username. Unmatched names default to the meeting creator.

## Project Structure

```
backend/
├── apps/
│   ├── users/
│   ├── teams/
│   ├── meetings/
│   ├── tasks/
│   └── notifications/
├── config/
├── core/
└── requirements/
```

## Deployment

Production deployment uses Docker Compose with PostgreSQL, Redis, Gunicorn, WhiteNoise, and Celery. See [backend/deploy/DEPLOYMENT.md](backend/deploy/DEPLOYMENT.md) for build commands, environment variables, and reverse-proxy notes.

## CI/CD

GitHub Actions workflows:

- **CI** – Django check, migrations, tests, Docker image build (on push/PR to `main` or `master`)
- **Publish Docker image** – build and push to GitHub Container Registry (`ghcr.io`) on pushes to the default branch, version tags `v*`, or manual run

Details: [backend/deploy/CI_CD.md](backend/deploy/CI_CD.md).

## License

MIT
