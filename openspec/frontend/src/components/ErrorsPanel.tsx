import type { RunResponse } from "../types";

type ErrorsPanelProps = {
  result: RunResponse | null;
};

export function ErrorsPanel({ result }: ErrorsPanelProps) {
  if (!result) {
    return <div className="panel-empty">No diagnostics yet.</div>;
  }

  if (result.ok && result.diagnostics.length === 0) {
    return <div className="panel-empty">No errors.</div>;
  }

  return (
    <div className="panel-content">
      <div className="meta-row">
        <span>Status: {result.status}</span>
      </div>

      {result.diagnostics.map((diagnostic, idx) => (
        <div key={`${diagnostic.stage}-${idx}`} className="diagnostic-item">
          <strong>{diagnostic.stage}</strong>
          <p>{diagnostic.message}</p>
          <small>
            line: {diagnostic.line ?? "-"}, col: {diagnostic.column ?? "-"}
          </small>
        </div>
      ))}

      {result.stderr ? (
        <>
          <h4>stderr</h4>
          <pre>{result.stderr}</pre>
          {result.truncated?.stderr ? <p>stderr was truncated.</p> : null}
        </>
      ) : null}

      {result.stages ? (
        <>
          <h4>stages</h4>
          <pre>{JSON.stringify(result.stages, null, 2)}</pre>
        </>
      ) : null}
    </div>
  );
}
