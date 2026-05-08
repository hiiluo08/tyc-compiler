import { useEffect, useState } from 'react';

type AstPanelProps = {
  astJson: unknown | null;
  astText: string | null;
};

type AstViewMode = 'tree' | 'text';

function AstNode({ label, value }: { label?: string; value: unknown }) {
  if (value === null || value === undefined) {
    return (
      <li className="ast-tree-node">
        {label ? <span className="ast-node-key">{label}</span> : null}
        <span className="ast-node-value">null</span>
      </li>
    );
  }

  if (typeof value !== 'object') {
    return (
      <li className="ast-tree-node">
        {label ? <span className="ast-node-key">{label}</span> : null}
        <span className="ast-node-value">{String(value)}</span>
      </li>
    );
  }

  if (Array.isArray(value)) {
    return (
      <li className="ast-tree-node">
        {label ? <span className="ast-node-key">{label}</span> : null}
        <span className="ast-node-kind">Array[{value.length}]</span>
        {value.length > 0 ? (
          <ul className="ast-children">
            {value.map((item, index) => (
              <AstNode key={index} label={`[${index}]`} value={item} />
            ))}
          </ul>
        ) : null}
      </li>
    );
  }

  const obj = value as Record<string, unknown>;
  const kind = typeof obj.kind === 'string' ? obj.kind : undefined;
  const entries = Object.entries(obj).filter(
    ([key]) => key !== 'kind' && key !== 'line' && key !== 'column'
  );

  return (
    <li className="ast-tree-node">
      {label ? <span className="ast-node-key">{label}</span> : null}
      <span className="ast-node-kind">{kind ?? 'Object'}</span>
      {entries.length > 0 ? (
        <ul className="ast-children">
          {entries.map(([key, child]) => (
            <AstNode key={key} label={key} value={child} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export default function AstPanel({ astJson, astText }: AstPanelProps) {
  const [viewMode, setViewMode] = useState<AstViewMode>(astJson ? 'tree' : 'text');

  useEffect(() => {
    if (astJson) {
      setViewMode('tree');
    } else if (astText) {
      setViewMode('text');
    }
  }, [astJson, astText]);

  if (!astJson && !astText) {
    return <p className="result-block">No AST available.</p>;
  }

  const canShowTree = Boolean(astJson);
  const canShowText = Boolean(astText);

  return (
    <div className="result-block">
      <div className="ast-view-tabs">
        {canShowTree ? (
          <button type="button" className={viewMode === 'tree' ? 'active' : ''} onClick={() => setViewMode('tree')}>
            AST Tree
          </button>
        ) : null}
        {canShowText ? (
          <button type="button" className={viewMode === 'text' ? 'active' : ''} onClick={() => setViewMode('text')}>
            AST Text
          </button>
        ) : null}
      </div>

      {viewMode === 'tree' && astJson ? (
        <ul className="ast-tree">
          <AstNode value={astJson} />
        </ul>
      ) : null}

      {viewMode === 'text' && astText ? <pre>{astText}</pre> : null}
    </div>
  );
}
