# Deployment Guide — TyC Web Compiler (GSD Variant)

## Architecture

- Frontend: Vercel-hosted Vite app from `gsd/frontend/`.
- Runner API: Dockerized FastAPI service from `gsd/runner/` on an external host.

## Frontend deployment (Vercel)

Use these Vercel project settings:

- Framework Preset: `Vite`
- Root Directory: `gsd/frontend`
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: `dist`

Set environment variables in Vercel:

- `VITE_TYC_API_BASE_URL=https://<runner-api-origin>`
- `VITE_DEFAULT_TIMEOUT_SECONDS=3`

## Runner deployment (Docker)

### Build image

From repository root:

```bash
docker build -f gsd/runner/Dockerfile -t tyc-runner-gsd .
```

### Run container

```bash
docker run --rm -p 8000:8000 \
  --env-file gsd/runner/.env.example \
  tyc-runner-gsd
```

Runner endpoint health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"ok":true,"service":"tyc-runner-gsd","version":"0.1.0"}
```

## Required runner environment variables

- `TYC_ALLOWED_ORIGINS=https://<vercel-origin>`
- `TYC_DEFAULT_TIMEOUT_SECONDS=3`
- `TYC_MAX_TIMEOUT_SECONDS=5`
- `TYC_MAX_SOURCE_BYTES=65536`
- `TYC_MAX_STDIN_BYTES=16384`
- `TYC_MAX_OUTPUT_BYTES=32768`
- `TYC_MAX_CONCURRENT_RUNS=2`

## Public safety recommendations

- Set CORS allowlist to the exact deployed Vercel origin.
- Run runner with CPU and memory limits at container/platform level.
- Avoid writable host mounts for user-executed workspace paths.
- Disable outbound network for execution sandbox where platform supports it.
- Add rate limiting before opening public access.

## Operational notes

- Frontend and runner must be deployed independently.
- `VITE_TYC_API_BASE_URL` should always point to the public HTTPS runner URL.
- Keep runner logs focused on request id, status, stage, duration; avoid logging full source by default.
