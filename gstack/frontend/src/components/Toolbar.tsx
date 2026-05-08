import { useRef } from 'react';
import type { Sample } from '../types';

type ToolbarProps = {
  running: boolean;
  selectedSample: string;
  samples: Sample[];
  onRun: () => void;
  onClear: () => void;
  onSampleChange: (name: string) => void;
  onLoadFile: (file: File) => void;
};

export default function Toolbar({
  running,
  selectedSample,
  samples,
  onRun,
  onClear,
  onSampleChange,
  onLoadFile
}: ToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div className="toolbar">
      <button className="toolbar-button toolbar-primary" disabled={running} onClick={onRun} type="button">
        <span className="button-icon" aria-hidden="true">
          {running ? (
            <svg className="button-icon-svg" viewBox="0 0 16 16">
              <path d="M8 1.6a.8.8 0 0 1 .8.8v5.2l3.4 2.04a.8.8 0 0 1-.8 1.38L7.6 8.74A.8.8 0 0 1 7.2 8V2.4a.8.8 0 0 1 .8-.8Z" />
            </svg>
          ) : (
            <svg className="button-icon-svg" viewBox="0 0 16 16">
              <path d="M5.1 3.1c0-.64.7-1.04 1.26-.72l6.15 3.56a.83.83 0 0 1 0 1.44l-6.15 3.56a.83.83 0 0 1-1.26-.72V3.1Z" />
            </svg>
          )}
        </span>
        <span>{running ? 'Running...' : 'Run'}</span>
      </button>

      <button className="toolbar-button" disabled={running} onClick={() => fileInputRef.current?.click()} type="button">
        <span className="button-icon" aria-hidden="true">
          <svg className="button-icon-svg" viewBox="0 0 16 16">
            <path d="M1.8 4.1c0-.72.58-1.3 1.3-1.3h3.03c.33 0 .64.16.84.43l.57.76h5.37c.72 0 1.3.58 1.3 1.3v5.6c0 .72-.58 1.3-1.3 1.3H3.1a1.3 1.3 0 0 1-1.3-1.3V4.1Zm4.2 2.53V8H4.54a.75.75 0 1 0 0 1.5H6v1.37a.75.75 0 1 0 1.5 0V9.5h1.37a.75.75 0 1 0 0-1.5H7.5V6.63a.75.75 0 1 0-1.5 0Z" />
          </svg>
        </span>
        <span>Load File</span>
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".tyc"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            onLoadFile(file);
          }
          event.currentTarget.value = '';
        }}
      />

      <select
        className="sample-select"
        value={selectedSample}
        onChange={(event) => onSampleChange(event.target.value)}
        disabled={running}
      >
        <option value="">Sample</option>
        {samples.map((sample) => (
          <option key={sample.name} value={sample.name}>
            {sample.name}
          </option>
        ))}
      </select>

      <button className="toolbar-button" disabled={running} onClick={onClear} type="button">
        <span className="button-icon" aria-hidden="true">
          <svg className="button-icon-svg" viewBox="0 0 16 16">
            <path d="M4.17 4.17a.8.8 0 0 1 1.13 0L8 6.87l2.7-2.7a.8.8 0 0 1 1.13 1.13L9.13 8l2.7 2.7a.8.8 0 0 1-1.13 1.13L8 9.13l-2.7 2.7a.8.8 0 1 1-1.13-1.13l2.7-2.7-2.7-2.7a.8.8 0 0 1 0-1.13Z" />
          </svg>
        </span>
        <span>Clear</span>
      </button>
    </div>
  );
}
