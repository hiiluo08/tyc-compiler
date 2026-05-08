import type { AstRequest, AstResponse, RunRequest, RunResponse } from './types';

const DEFAULT_TIMEOUT_SECONDS = Number(import.meta.env.VITE_DEFAULT_TIMEOUT_SECONDS ?? 3);

function resolveApiBaseUrl(): string {
  const base = import.meta.env.VITE_TYC_API_BASE_URL as string | undefined;
  if (base && base.trim().length > 0) {
    return base.replace(/\/$/, '');
  }

  if (import.meta.env.PROD) {
    throw new Error('Missing VITE_TYC_API_BASE_URL in production mode.');
  }

  return 'http://127.0.0.1:8000';
}

function isOfflineError(error: unknown): boolean {
  if (!(error instanceof Error)) {
    return false;
  }
  return /fetch|network|failed to fetch|load failed/i.test(error.message);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

async function postJson<TReq, TRes>(path: string, payload: TReq, timeoutSeconds = DEFAULT_TIMEOUT_SECONDS): Promise<TRes> {
  const base = resolveApiBaseUrl();
  const controller = new AbortController();
  const timeoutMs = Math.max(1000, (timeoutSeconds + 2) * 1000);
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${base}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    return (await response.json()) as TRes;
  } finally {
    clearTimeout(timer);
  }
}

export async function runProgram(payload: RunRequest): Promise<RunResponse> {
  const request: RunRequest = {
    source: payload.source,
    stdin: payload.stdin ?? '',
    timeoutSeconds: payload.timeoutSeconds ?? DEFAULT_TIMEOUT_SECONDS,
    includeAst: payload.includeAst ?? true
  };

  return postJson<RunRequest, RunResponse>('/api/v1/run', request, request.timeoutSeconds);
}

export async function getAst(payload: AstRequest): Promise<AstResponse> {
  return postJson<AstRequest, AstResponse>('/api/v1/ast', payload);
}

export class ApiOfflineError extends Error {
  constructor(message = 'Runner API is offline.') {
    super(message);
    this.name = 'ApiOfflineError';
  }
}

export class ApiRequestTimeoutError extends Error {
  constructor(message = 'Runner API request timed out.') {
    super(message);
    this.name = 'ApiRequestTimeoutError';
  }
}

export function normalizeClientError(error: unknown): Error {
  if (isAbortError(error)) {
    return new ApiRequestTimeoutError();
  }

  if (isOfflineError(error)) {
    return new ApiOfflineError();
  }

  if (error instanceof Error) {
    return error;
  }

  return new Error('Unexpected client error.');
}