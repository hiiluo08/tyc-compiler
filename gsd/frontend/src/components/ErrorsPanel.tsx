import type { Diagnostic, StageMap, Status } from '../types';

type ErrorsPanelProps = {
  status: Status;
  diagnostics: Diagnostic[];
  stderr: string;
  stages: StageMap;
  errorMessage?: string;
};

export default function ErrorsPanel({ status, diagnostics, stderr, stages, errorMessage }: ErrorsPanelProps) {
  return (
    <div className="result-block">
      <p>
        <strong>Status:</strong> {status}
      </p>
      {errorMessage ? <p className="error-text">{errorMessage}</p> : null}
      <h3>Stages</h3>
      <ul>
        {Object.entries(stages).map(([stage, stageStatus]) => (
          <li key={stage}>
            {stage}: {stageStatus}
          </li>
        ))}
      </ul>
      <h3>Diagnostics</h3>
      {diagnostics.length === 0 ? (
        <p>(no diagnostics)</p>
      ) : (
        <ul>
          {diagnostics.map((diag, index) => (
            <li key={`${diag.stage}-${index}`}>
              [{diag.stage}] {diag.message}
            </li>
          ))}
        </ul>
      )}
      {stderr ? (
        <>
          <h3>Stderr</h3>
          <pre>{stderr}</pre>
        </>
      ) : null}
    </div>
  );
}