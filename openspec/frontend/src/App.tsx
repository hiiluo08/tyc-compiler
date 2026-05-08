import { useState } from "react";
import { runProgram } from "./api";
import { CodeEditor } from "./components/CodeEditor";
import { ResultPanel, type ResultTab } from "./components/ResultPanel";
import { StdinPanel } from "./components/StdinPanel";
import { Toolbar } from "./components/Toolbar";
import { samples } from "./samples";
import type { RunResponse } from "./types";

const DEFAULT_TIMEOUT = Number(import.meta.env.VITE_DEFAULT_TIMEOUT_SECONDS ?? "3");

type UiState = "idle" | "running" | "success" | "error" | "timeout" | "api_offline";

function formatUiStateLabel(state: UiState): string {
  return state.replace(/_/g, " ");
}

export function App() {
  const [source, setSource] = useState("");
  const [stdin, setStdin] = useState("");
  const [selectedSample, setSelectedSample] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [tab, setTab] = useState<ResultTab>("output");
  const [uiState, setUiState] = useState<UiState>("idle");

  const doRun = async () => {
    setRunning(true);
    setUiState("running");
    try {
      const response = await runProgram({
        source,
        stdin,
        timeoutSeconds: DEFAULT_TIMEOUT,
        includeAst: true,
      });
      setResult(response);
      if (response.ok) {
        setUiState("success");
      } else if (response.status === "timeout") {
        setUiState("timeout");
      } else {
        setUiState("error");
      }
      setTab(response.ok ? "output" : "errors");
    } catch (error) {
      setUiState("api_offline");
      setResult({
        ok: false,
        status: "internal_error",
        stdout: "",
        stderr: "",
        diagnostics: [
          {
            stage: "internal",
            severity: "error",
            message: error instanceof Error ? error.message : "API offline",
            line: null,
            column: null,
            raw: String(error),
          },
        ],
        astText: null,
        astJson: null,
        stages: null,
        durationMs: 0,
        truncated: { stdout: false, stderr: false },
      });
      setTab("errors");
    } finally {
      setRunning(false);
    }
  };

  const handleSampleChange = (name: string) => {
    setSelectedSample(name);
    if (!name) {
      setSource("");
      setStdin("");
      return;
    }

    const sample = samples.find((item) => item.name === name);
    if (!sample) return;
    setSource(sample.source);
    setStdin(sample.stdin);
  };

  const handleLoadFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".tyc")) {
      return;
    }

    const content = await file.text();
    setSource(content);
    setStdin("");
    setSelectedSample("");
    setResult(null);
    setUiState("idle");
    setTab("output");
  };

  const clearAll = () => {
    setSource("");
    setStdin("");
    setSelectedSample("");
    setResult(null);
    setUiState("idle");
    setTab("output");
  };

  return (
    <main className="page">
      <header>
        <h1 className="brand-title">
          <span className="brand-accent">TyC</span>
          <span>Web Compiler</span>
        </h1>
        <div className="header-controls">
          <p className={`status-badge status-${uiState}`}>
            <span>status: {formatUiStateLabel(uiState)}</span>
            <span className={`status-dot status-dot-${uiState}`} aria-hidden="true" />
          </p>
          <button className="header-icon-button" type="button" aria-label="Theme settings">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3.6a.8.8 0 0 1 .76.54l.92 2.76a6.8 6.8 0 0 1 3.42 1.41l2.83-.57a.8.8 0 0 1 .88.38.8.8 0 0 1-.1.95l-1.9 2.15c.24.68.36 1.41.36 2.18 0 .77-.12 1.5-.36 2.18l1.9 2.15a.8.8 0 0 1 .1.95.8.8 0 0 1-.88.38l-2.83-.57a6.8 6.8 0 0 1-3.42 1.41l-.92 2.76a.8.8 0 0 1-1.52 0l-.92-2.76a6.8 6.8 0 0 1-3.42-1.41l-2.83.57a.8.8 0 0 1-.88-.38.8.8 0 0 1 .1-.95l1.9-2.15A6.5 6.5 0 0 1 4.9 13c0-.77.12-1.5.36-2.18l-1.9-2.15a.8.8 0 0 1-.1-.95.8.8 0 0 1 .88-.38l2.83.57a6.8 6.8 0 0 1 3.42-1.41l.92-2.76a.8.8 0 0 1 .76-.54Zm0 5a4.4 4.4 0 1 0 0 8.8 4.4 4.4 0 0 0 0-8.8Z" />
            </svg>
          </button>
        </div>
      </header>

      <Toolbar
        running={running}
        selectedSample={selectedSample}
        samples={samples}
        onRun={doRun}
        onClear={clearAll}
        onSampleChange={handleSampleChange}
        onLoadFile={handleLoadFile}
      />

      <section className="workspace-grid">
        <div>
          <CodeEditor value={source} onChange={setSource} />
        </div>
        <ResultPanel tab={tab} onTabChange={setTab} result={result} />
      </section>

      <StdinPanel value={stdin} onChange={setStdin} />
    </main>
  );
}
