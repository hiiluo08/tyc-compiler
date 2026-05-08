import Editor from "@monaco-editor/react";

type CodeEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export function CodeEditor({ value, onChange }: CodeEditorProps) {
  return (
    <div className="code-editor-shell">
      <Editor
        height="380px"
        defaultLanguage="c"
        theme="vs-dark"
        value={value}
        onChange={(next) => onChange(next ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 15,
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
          lineNumbersMinChars: 2,
          tabSize: 4,
          wordWrap: "on",
          automaticLayout: true,
          scrollBeyondLastLine: false,
          glyphMargin: false,
          folding: false,
        }}
      />
    </div>
  );
}
