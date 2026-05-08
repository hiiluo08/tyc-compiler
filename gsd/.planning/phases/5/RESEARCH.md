# Phase 5: Deployment docs/config for Vercel frontend and Docker runner - Research

**Researched:** 2026-05-07  
**Domain:** Deployment packaging and configuration for TyC webapp split architecture  
**Confidence:** HIGH

## Summary

Phase 5 should formalize deployment shape already implied by spec and current implementation:
- frontend deploy on Vercel from `gsd/frontend/`,
- runner deploy as separate Dockerized FastAPI service from `gsd/runner/`.

Primary deliverables are operational docs + Dockerfile, not product behavior changes.

## Key decisions to implement
- Keep Vercel and runner separated.
- Provide non-root runner Docker image with Java runtime and Python deps.
- Document all required env variables and minimal run commands.
- Include CORS origin guidance and runtime safety notes.

## Practical guidance

### Frontend
- Build command: `npm run build`.
- Output dir: `dist`.
- Required env: `VITE_TYC_API_BASE_URL`.

### Runner
- Base image: `python:3.12-slim`.
- Install OpenJDK headless for Jasmin/JVM execution.
- Install `gsd/runner/requirements-web.txt`.
- Run `uvicorn runner.app.main:app --host 0.0.0.0 --port 8000`.
- Use non-root user.

## Verification guidance
- `cd gsd/frontend && npm run build`
- `docker build -f gsd/runner/Dockerfile .` (or context-adjusted equivalent)
- Validate docs include env keys + example configuration.
- Validate no non-`gsd/` changes.

## Exit signal
Research is sufficient for an executable Phase 5 plan focused on Dockerfile + deployment docs + config examples + verification checks.
