import type { RunRequest, RunResponse } from "./types";

const envBaseUrl = import.meta.env.VITE_TYC_API_BASE_URL as string | undefined;

if (import.meta.env.PROD && !envBaseUrl) {
  throw new Error("Missing VITE_TYC_API_BASE_URL for production build.");
}

const API_BASE_URL = envBaseUrl ?? "http://localhost:8000";

async function postJson<TPayload, TResult>(path: string, payload: TPayload): Promise<TResult> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as TResult;
}

export function runProgram(payload: RunRequest): Promise<RunResponse> {
  return postJson<RunRequest, RunResponse>("/api/v1/run", payload);
}

export function generateAst(source: string): Promise<RunResponse> {
  return postJson<{ source: string }, RunResponse>("/api/v1/ast", { source });
}
