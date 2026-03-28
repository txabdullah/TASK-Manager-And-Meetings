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

## Continuous deployment

There is no default deploy job: hosting (VPS, Kubernetes, Railway, etc.) differs per project.

Typical options:

1. **SSH**: workflow step that SSHs to the server and runs `docker compose pull && docker compose up -d` (store host, user, and key in GitHub **Secrets**).
2. **Kubernetes**: `kubectl set image` or Helm upgrade using a cluster secret.
3. **Platform**: connect the repo to Railway, Render, or Fly.io and point them at `backend/Dockerfile` or the published GHCR image.

Add a new workflow file under `.github/workflows/` when you choose an approach.
