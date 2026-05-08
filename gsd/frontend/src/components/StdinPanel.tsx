type StdinPanelProps = {
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
};

export default function StdinPanel({ value, onChange, disabled }: StdinPanelProps) {
  return (
    <section className="panel stdin-panel">
      <h2>Stdin</h2>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        placeholder="Optional stdin input"
        rows={5}
      />
    </section>
  );
}