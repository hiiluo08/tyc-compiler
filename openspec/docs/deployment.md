# Deployment Guide (OpenSpec TyC Web Compiler)

## Architecture
- Frontend: `openspec/frontend` deploy on Vercel.
- Runner: `openspec/runner` deploy as Docker service on an external host.

## 1) Deploy frontend to Vercel

Use these settings:
- Framework Preset: `Vite`
- Root Directory: `openspec/frontend`
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: `dist`

Frontend environment variables:
- `VITE_TYC_API_BASE_URL=https://<runner-origin>`
- `VITE_DEFAULT_TIMEOUT_SECONDS=3`

## 2) Build and deploy runner

Build image from repository root:

```bash
docker build -f openspec/runner/Dockerfile -t tyc-runner-openspec .
```

Run container:

```bash
docker run --rm -p 8000:8000 \
  -e TYC_ALLOWED_ORIGINS=https://<your-vercel-origin> \
  -e TYC_DEFAULT_TIMEOUT_SECONDS=3 \
  -e TYC_MAX_TIMEOUT_SECONDS=5 \
  -e TYC_MAX_SOURCE_BYTES=65536 \
  -e TYC_MAX_STDIN_BYTES=16384 \
  -e TYC_MAX_OUTPUT_BYTES=32768 \
  -e TYC_MAX_CONCURRENT_RUNS=2 \
  tyc-runner-openspec
```

Runner endpoints:
- `GET /health`
- `POST /api/v1/run`
- `POST /api/v1/ast`

## 3) Public safety checklist
- Restrict CORS allowlist to deployed Vercel origin.
- Keep timeout/output limits enabled.
- Keep container as non-root user.
- Add platform CPU/memory limits.
- Add rate limit at ingress before public launch.
- Disable outbound network for execution container if platform supports it.
