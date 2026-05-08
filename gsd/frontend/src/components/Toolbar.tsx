import type { Sample } from '../types';

type ToolbarProps = {
  running: boolean;
  samples: Sample[];
  onRun: () => void;
  onClear: () => void;
  onLoadSample: (sample: Sample) => void;
};

export default function Toolbar({ running, samples, onRun, onClear, onLoadSample }: ToolbarProps) {
  return (
    <div className="toolbar">
      <button type="button" onClick={onRun} disabled={running}>
        {running ? 'Running...' : 'Run'}
      </button>
      <button type="button" onClick={onClear} disabled={running}>
        Clear
      </button>
      <label>
        Load Sample
        <select
          defaultValue=""
          onChange={(event) => {
            const name = event.target.value;
            const selected = samples.find((sample) => sample.name === name);
            if (selected) {
              onLoadSample(selected);
            }
          }}
          disabled={running}
        >
          <option value="" disabled>
            Select sample
          </option>
          {samples.map((sample) => (
            <option key={sample.name} value={sample.name}>
              {sample.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}