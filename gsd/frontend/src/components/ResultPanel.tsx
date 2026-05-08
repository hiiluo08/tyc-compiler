import type { RunResponse, UiState } from '../types';
import AstPanel from './AstPanel';
import ErrorsPanel from './ErrorsPanel';
import OutputPanel from './OutputPanel';

type Tab = 'output' | 'errors' | 'ast';

type ResultPanelProps = {
  state: UiState;
  result: RunResponse | null;
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  errorMessage: string;
};

const EMPTY_STAGES = {
  parse: 'pending',
  ast: 'pending',
  semantic: 'pending',
  codegen: 'pending',
  assemble: 'pending',
  run: 'pending'
} as const;

export default function ResultPanel({ state, result, activeTab, onTabChange, errorMessage }: ResultPanelProps) {
  return (
    <section className="panel result-panel">
      <h2>Result Panel</h2>
      <p>
        <strong>State:</strong> {state}
      </p>
      <div className="tabs">
        <button type="button" className={activeTab === 'output' ? 'active' : ''} onClick={() => onTabChange('output')}>
          Output
        </button>
        <button type="button" className={activeTab === 'errors' ? 'active' : ''} onClick={() => onTabChange('errors')}>
          Errors
        </button>
        <button type="button" className={activeTab === 'ast' ? 'active' : ''} onClick={() => onTabChange('ast')}>
          AST
        </button>
      </div>

      {activeTab === 'output' ? (
        <OutputPanel stdout={result?.stdout ?? ''} durationMs={result?.durationMs ?? 0} />
      ) : null}

      {activeTab === 'errors' ? (
        <ErrorsPanel
          status={result?.status ?? 'internal_error'}
          diagnostics={result?.diagnostics ?? []}
          stderr={result?.stderr ?? ''}
          stages={result?.stages ?? EMPTY_STAGES}
          errorMessage={errorMessage}
        />
      ) : null}

      {activeTab === 'ast' ? <AstPanel astJson={result?.astJson ?? null} astText={result?.astText ?? null} /> : null}
    </section>
  );
}