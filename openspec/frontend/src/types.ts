export type RunStatus =
  | "success"
  | "lexical_error"
  | "syntax_error"
  | "ast_error"
  | "semantic_error"
  | "codegen_error"
  | "assembly_error"
  | "runtime_error"
  | "timeout"
  | "input_too_large"
  | "internal_error";

export type StageState = "success" | "failed" | "skipped";

export type Diagnostic = {
  stage: "lex" | "parse" | "ast" | "semantic" | "codegen" | "assemble" | "run" | "internal";
  severity: "error" | "warning";
  message: string;
  line: number | null;
  column: number | null;
  raw: string;
};

export type TruncatedFlags = {
  stdout: boolean;
  stderr: boolean;
};

export type RunResponse = {
  ok: boolean;
  status: RunStatus;
  stdout: string;
  stderr: string;
  diagnostics: Diagnostic[];
  astText: string | null;
  astJson: unknown;
  stages?: Record<string, StageState> | null;
  durationMs: number;
  truncated?: TruncatedFlags | null;
};

export type RunRequest = {
  source: string;
  stdin?: string;
  timeoutSeconds?: number;
  includeAst?: boolean;
};
