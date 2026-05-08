type StdinPanelProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function StdinPanel({ value, onChange }: StdinPanelProps) {
  return (
    <div className="stdin-panel">
      <label htmlFor="stdin">Stdin</label>
      <textarea
        id="stdin"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Optional stdin for readInt/readFloat/readString"
      />
    </div>
  );
}
