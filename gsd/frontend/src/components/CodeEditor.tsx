import Editor from '@monaco-editor/react';

type CodeEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function CodeEditor({ value, onChange }: CodeEditorProps) {
  return (
    <section className="panel code-panel">
      <h2>Code Editor</h2>
      <Editor
        height="420px"
        defaultLanguage="cpp"
        value={value}
        options={{
          tabSize: 4,
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false
        }}
        onChange={(next) => onChange(next ?? '')}
      />
    </section>
  );
}