import type { RunResponse } from '../types';
import AstPanel from './AstPanel';
import ErrorsPanel from './ErrorsPanel';
import OutputPanel from './OutputPanel';

export type ResultTab = 'output' | 'errors' | 'ast';

type ResultPanelProps = {
  tab: ResultTab;
  onTabChange: (tab: ResultTab) => void;
  result: RunResponse | null;
};

export default function ResultPanel({ tab, onTabChange, result }: ResultPanelProps) {
  return (
    <div className="result-panel">
      <div className="tabs">
        <button className={tab === 'output' ? 'tab-active' : ''} onClick={() => onTabChange('output')} type="button">
          Output
        </button>
        <button className={tab === 'errors' ? 'tab-active' : ''} onClick={() => onTabChange('errors')} type="button">
          Errors
        </button>
        <button className={tab === 'ast' ? 'tab-active' : ''} onClick={() => onTabChange('ast')} type="button">
          AST
        </button>
      </div>

      {tab === 'output' ? <OutputPanel result={result} /> : null}
      {tab === 'errors' ? <ErrorsPanel result={result} /> : null}
      {tab === 'ast' ? <AstPanel result={result} /> : null}
    </div>
  );
}
