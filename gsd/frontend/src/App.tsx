import { useState } from 'react';
import { ApiOfflineError, ApiRequestTimeoutError, normalizeClientError, runProgram } from './api';
import CodeEditor from './components/CodeEditor';
import ResultPanel from './components/ResultPanel';
import StdinPanel from './components/StdinPanel';
import Toolbar from './components/Toolbar';
import { samples } from './samples';
import type { RunResponse, Sample, UiState } from './types';

type Tab = 'output' | 'errors' | 'ast';

function mapUiState(result: RunResponse): UiState {
  if (result.status === 'success') {
    return 'success';
  }
  if (result.status === 'timeout') {
    return 'timeout';
  }
  return 'error';
}

export default function App() {
  const initial = samples[0];
  const [source, setSource] = useState<string>(initial.source);
  const [stdin, setStdin] = useState<string>(initial.stdin);
  const [uiState, setUiState] = useState<UiState>('idle');
  const [activeTab, setActiveTab] = useState<Tab>('output');
  const [result, setResult] = useState<RunResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const running = uiState === 'running';

  const handleLoadSample = (sample: Sample) => {
    setSource(sample.source);
    setStdin(sample.stdin);
  };

  const handleClear = () => {
    setSource('');
    setStdin('');
    setUiState('idle');
    setResult(null);
    setErrorMessage('');
    setActiveTab('output');
  };

  const handleRun = async () => {
    setUiState('running');
    setErrorMessage('');
    setActiveTab('output');

    try {
      const response = await runProgram({
        source,
        stdin,
        includeAst: true
      });
      setResult(response);
      setUiState(mapUiState(response));
      if (response.status !== 'success') {
        setActiveTab('errors');
      }
    } catch (error) {
      const normalized = normalizeClientError(error);
      setResult(null);
      if (normalized instanceof ApiRequestTimeoutError) {
        setUiState('timeout');
        setErrorMessage('Request timed out while waiting for runner response.');
      } else if (normalized instanceof ApiOfflineError) {
        setUiState('api_offline');
        setErrorMessage('Cannot connect to runner API. Please check service availability.');
      } else {
        setUiState('error');
        setErrorMessage(normalized.message);
      }
      setActiveTab('errors');
    }
  };

  return (
    <main className="app-shell">
      <header>
        <h1>TyC Web Compiler - GSD Variant</h1>
      </header>

      <Toolbar
        running={running}
        samples={samples}
        onRun={handleRun}
        onClear={handleClear}
        onLoadSample={handleLoadSample}
      />

      <section className="grid-layout">
        <CodeEditor value={source} onChange={setSource} />
        <ResultPanel state={uiState} result={result} activeTab={activeTab} onTabChange={setActiveTab} errorMessage={errorMessage} />
      </section>

      <StdinPanel value={stdin} onChange={setStdin} disabled={running} />
    </main>
  );
}