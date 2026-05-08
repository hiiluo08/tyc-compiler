# Deployment Guide

## Topology
- Frontend: Vercel (`gstack/frontend`)
- Runner API: Docker-capable host (`gstack/runner`)

## 1) Deploy runner

### Build image
```bash
docker build -f gstack/runner/Dockerfile -t tyc-runner-gstack .
```

### Run container
```bash
docker run --rm -p 8000:8000 \
  -e TYC_ALLOWED_ORIGINS=https://<your-vercel-domain> \
  -e TYC_DEFAULT_TIMEOUT_SECONDS=3 \
  -e TYC_MAX_TIMEOUT_SECONDS=5 \
  -e TYC_MAX_SOURCE_BYTES=65536 \
  -e TYC_MAX_STDIN_BYTES=16384 \
  -e TYC_MAX_OUTPUT_BYTES=32768 \
  -e TYC_MAX_CONCURRENT_RUNS=2 \
  tyc-runner-gstack
```

### Smoke check
```bash
curl http://127.0.0.1:8000/health
```
Expected:
```json
{"ok":true,"service":"tyc-runner-gstack","version":"0.1.0"}
```

## 2) Deploy frontend on Vercel

Vercel settings:
- Framework preset: `Vite`
- Root directory: `gstack/frontend`
- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: `dist`

Environment variables:
- `VITE_TYC_API_BASE_URL=https://<runner-public-origin>`
- `VITE_DEFAULT_TIMEOUT_SECONDS=3`

## 3) Pre-ship checklist
- [ ] Runner `/health` is public and healthy.
- [ ] CORS allowlist includes only your frontend domain(s).
- [ ] Timeout/size/output/concurrency env values set.
- [ ] `npm --prefix gstack/frontend run build` succeeds.
- [ ] `PYTHONPATH=gstack venv/Scripts/python.exe -m pytest gstack/tests -q` passes.

## 4) Known limitations
1. No authentication in v1.
2. No request rate limiting middleware in v1.
3. Sandbox/network hardening depends on deployment platform controls.
