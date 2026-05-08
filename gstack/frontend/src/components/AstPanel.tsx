import { useMemo, useState } from 'react';
import type { RunResponse } from '../types';

type AstPanelProps = {
  result: RunResponse | null;
};

type AstViewMode = 'tree' | 'text';

type AstJsonNode = {
  kind: string;
  fields?: Record<string, unknown>;
};

function isAstNode(value: unknown): value is AstJsonNode {
  if (!value || typeof value !== 'object') {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return typeof candidate.kind === 'string';
}

function normalizeValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeValue(item));
  }

  if (isAstNode(value)) {
    const rawFields = value.fields && typeof value.fields === 'object' ? value.fields : {};
    const filteredEntries = Object.entries(rawFields).filter(([key]) => key !== 'line' && key !== 'column');
    const normalizedFields: Record<string, unknown> = {};

    for (const [key, fieldValue] of filteredEntries) {
      normalizedFields[key] = normalizeValue(fieldValue);
    }

    return {
      kind: value.kind,
      fields: normalizedFields
    } satisfies AstJsonNode;
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .filter(([key]) => key !== 'line' && key !== 'column')
      .map(([key, child]) => [key, normalizeValue(child)] as const);

    return Object.fromEntries(entries);
  }

  return value;
}

function renderPrimitive(value: unknown): string {
  if (value === null) {
    return 'null';
  }
  if (typeof value === 'string') {
    return value;
  }
  return String(value);
}

function AstTreeValue({ label, value, depth }: { label: string; value: unknown; depth: number }) {
  const indentStyle = { marginLeft: `${depth * 12}px` };

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <div className="ast-leaf" style={indentStyle}>
          <span className="ast-key">{label}</span>
          <span className="ast-value">[]</span>
        </div>
      );
    }

    return (
      <details className="ast-node" open={depth < 2}>
        <summary style={indentStyle}>
          <span className="ast-key">{label}</span>
          <span className="ast-meta">[{value.length}]</span>
        </summary>
        <div className="ast-children">
          {value.map((item, index) => (
            <AstTreeValue key={`${label}-${index}`} label={`[${index}]`} value={item} depth={depth + 1} />
          ))}
        </div>
      </details>
    );
  }

  if (isAstNode(value)) {
    const fields = value.fields ?? {};
    const entries = Object.entries(fields);

    return (
      <details className="ast-node" open={depth < 2}>
        <summary style={indentStyle}>
          <span className="ast-key">{label}</span>
          <span className="ast-kind">{value.kind}</span>
        </summary>
        <div className="ast-children">
          {entries.length === 0 ? (
            <div className="ast-leaf" style={{ marginLeft: `${(depth + 1) * 12}px` }}>
              <span className="ast-value">(empty)</span>
            </div>
          ) : (
            entries.map(([fieldKey, fieldValue]) => (
              <AstTreeValue key={`${label}-${fieldKey}`} label={fieldKey} value={fieldValue} depth={depth + 1} />
            ))
          )}
        </div>
      </details>
    );
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    return (
      <details className="ast-node" open={depth < 2}>
        <summary style={indentStyle}>
          <span className="ast-key">{label}</span>
          <span className="ast-meta">object</span>
        </summary>
        <div className="ast-children">
          {entries.map(([fieldKey, fieldValue]) => (
            <AstTreeValue key={`${label}-${fieldKey}`} label={fieldKey} value={fieldValue} depth={depth + 1} />
          ))}
        </div>
      </details>
    );
  }

  return (
    <div className="ast-leaf" style={indentStyle}>
      <span className="ast-key">{label}</span>
      <span className="ast-value">{renderPrimitive(value)}</span>
    </div>
  );
}

export default function AstPanel({ result }: AstPanelProps) {
  const [viewMode, setViewMode] = useState<AstViewMode>('tree');

  const astText = useMemo(() => {
    if (!result) {
      return 'Run or request AST to see tree data.';
    }
    if (result.astText) {
      return result.astText;
    }
    if (result.astJson) {
      return JSON.stringify(result.astJson, null, 2);
    }
    return 'No AST available.';
  }, [result]);

  const normalizedAst = useMemo(() => {
    if (!result?.astJson) {
      return null;
    }
    return normalizeValue(result.astJson);
  }, [result]);

  if (!result) {
    return <div className="panel-empty">Run or request AST to see tree data.</div>;
  }

  return (
    <div className="panel-content">
      <div className="ast-mode-switch" role="tablist" aria-label="AST view mode">
        <button className={viewMode === 'tree' ? 'ast-mode-active' : ''} onClick={() => setViewMode('tree')} type="button">
          Tree
        </button>
        <button className={viewMode === 'text' ? 'ast-mode-active' : ''} onClick={() => setViewMode('text')} type="button">
          AST Text
        </button>
      </div>

      {viewMode === 'text' ? (
        <pre>{astText}</pre>
      ) : normalizedAst ? (
        <div className="ast-tree ast-tree-ast">
          <AstTreeValue label="AST" value={normalizedAst} depth={0} />
        </div>
      ) : (
        <pre>{astText}</pre>
      )}
    </div>
  );
}
