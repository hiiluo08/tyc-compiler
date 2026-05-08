import type { RunResponse } from "../types";

type OutputPanelProps = {
  result: RunResponse | null;
};

export function OutputPanel({ result }: OutputPanelProps) {
  if (!result) {
    return <div className="panel-empty">Run a program to see output.</div>;
  }

  return (
    <div className="panel-content">
      <div className="meta-row">
        <span>Status: {result.status}</span>
        <span>Duration: {result.durationMs}ms</span>
      </div>
      <pre>{result.stdout || "<empty>"}</pre>
      {result.truncated?.stdout ? <p>stdout was truncated.</p> : null}
    </div>
  );
}
