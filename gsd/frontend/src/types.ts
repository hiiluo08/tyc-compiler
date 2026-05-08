export type Status =
  | 'success'
  | 'lexical_error'
  | 'syntax_error'
  | 'ast_error'
  | 'semantic_error'
  | 'codegen_error'
  | 'assembly_error'
  | 'runtime_error'
  | 'timeout'
  | 'input_too_large'
  | 'internal_error';

export type DiagnosticStage =
  | 'lex'
  | 'parse'
  | 'ast'
  | 'semantic'
  | 'codegen'
  | 'assemble'
  | 'run'
  | 'internal';

export type StageStatus = 'pending' | 'success' | 'failed' | 'skipped';

export type Diagnostic = {
  stage: DiagnosticStage;
  severity: 'error' | 'warning';
  message: string;
  line: number | null;
  column: number | null;
  raw: string;
};

export type StageMap = {
  parse: StageStatus;
  ast: StageStatus;
  semantic: StageStatus;
  codegen: StageStatus;
  assemble: StageStatus;
  run: StageStatus;
};

export type RunRequest = {
  source: string;
  stdin?: string;
  timeoutSeconds?: number;
  includeAst?: boolean;
};

export type AstRequest = {
  source: string;
};

export type ApiBaseResponse = {
  ok: boolean;
  status: Status;
  diagnostics: Diagnostic[];
  durationMs: number;
};

export type RunResponse = ApiBaseResponse & {
  stdout: string;
  stderr: string;
  astText: string | null;
  astJson: unknown | null;
  stages: StageMap;
  truncated?: {
    stdout: boolean;
    stderr: boolean;
  };
};

export type AstResponse = ApiBaseResponse & {
  astText: string | null;
  astJson: unknown | null;
};

export type UiState = 'idle' | 'running' | 'success' | 'error' | 'timeout' | 'api_offline';

export type Sample = {
  name: string;
  source: string;
  stdin: string;
};