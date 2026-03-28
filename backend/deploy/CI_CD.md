# CI/CD

## Continuous integration (`.github/workflows/ci.yml`)

Runs on every push and pull request to `main` or `master`:

1. Install Python 3.12 and dependencies from `requirements/base.txt`
2. `python manage.py check`
3. `python manage.py migrate`
4. `python manage.py test` (includes smoke tests under `apps/users/tests/`)
5. Redis service container (for settings that expect a broker URL)
6. **Docker**: builds the production `Dockerfile` (no push) with BuildKit cache

## Publish image (`.github/workflows/docker-publish.yml`)

Runs when:

- Code is pushed to the default branch (`main` / `master`)
- A tag matching `v*` is pushed (e.g. `v1.0.0`)
- You run the workflow manually (**Actions → Publish Docker image → Run workflow**)

Builds and pushes to **GitHub Container Registry**:

`ghcr.io/<owner>/<repo>/api`

Tags:

- `latest` on the default branch
- Git SHA
- Semantic version tags when you push `v*` tags

### Package visibility

After the first push, open the package in GitHub (**Packages** on the repo or org) and set visibility to **public** if external hosts should pull the image without authentication.

### Pull on a server

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/OWNER/REPO/api:latest
```

Use a Personal Access Token with `read:packages` (or `write:packages` for CI machines that also push).

## Continuous deployment — AWS EC2 (`.github/workflows/deploy-aws.yml`)

This workflow **SSHs into your server**, logs in to **GHCR**, pulls **`latest`**, and runs **Compose** with a small override so `web` / `celery` / `celery-beat` use the **pre-built image** instead of building on the host.

### Triggers

| Trigger | When it runs |
|--------|----------------|
| **Manual** | **Actions → Deploy to AWS (EC2) → Run workflow** |
| **After publish** | When **Publish Docker image** completes **successfully** |

To use **manual deploy only**, delete the `workflow_run:` block from `deploy-aws.yml` (keep `workflow_dispatch`).

### Approval before deploy

The deploy job uses GitHub **Environment** `production`. Configure **Settings → Environments → production → Required reviewers** so the job **waits for approval** before SSH runs. Without reviewers, the job runs immediately when triggered.

### One-time EC2 setup

1. Install **Docker Engine** and **Docker Compose plugin** (v2; merge override with `build: null` needs a recent Compose).
2. Copy onto the server (same layout as repo under `backend/`):
   - `docker-compose.prod.yml`
   - `deploy/docker-compose.ghcr.yml`
   - `deploy/.env.prod.example` → `.env` (real secrets, `ALLOWED_HOSTS`, DB passwords, etc.)
3. Point `AWS_DEPLOY_PATH` at the directory that **contains** `docker-compose.prod.yml` and the `deploy/` folder (e.g. `/opt/ai-task-manager/backend`).
4. Add the deploy SSH **public key** to `~/.ssh/authorized_keys` on the server; store the **private** key in `AWS_DEPLOY_SSH_KEY`.
5. Ensure the instance can **pull from GHCR** (`docker login` uses `GHCR_USERNAME` + `GHCR_READ_TOKEN` in the workflow).

### GitHub Actions secrets

| Secret | Purpose |
|--------|--------|
| `AWS_DEPLOY_HOST` | Server hostname or IP |
| `AWS_DEPLOY_USER` | SSH user (e.g. `ubuntu`, `ec2-user`) |
| `AWS_DEPLOY_SSH_KEY` | Private key PEM |
| `AWS_DEPLOY_PATH` | Absolute path to the `backend` directory on the server |
| `GHCR_USERNAME` | GitHub user for `docker login ghcr.io` |
| `GHCR_READ_TOKEN` | PAT with `read:packages` (and repo scope if the package is private) |

### Other hosting

1. **Kubernetes**: `kubectl set image` or Helm; use kubeconfig in secrets.
2. **PaaS** (Railway, Render, Fly): connect the repo or GHCR image; set env vars in the dashboard.

Add or adjust workflows under `.github/workflows/` as needed.
