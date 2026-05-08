type OutputPanelProps = {
  stdout: string;
  durationMs: number;
};

export default function OutputPanel({ stdout, durationMs }: OutputPanelProps) {
  return (
    <div className="result-block">
      <p>
        <strong>Duration:</strong> {durationMs} ms
      </p>
      <pre>{stdout || '(no output)'}</pre>
    </div>
  );
}