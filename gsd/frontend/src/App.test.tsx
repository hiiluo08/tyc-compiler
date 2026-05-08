import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';
import * as api from './api';
import type { RunResponse } from './types';

vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange }: { value: string; onChange: (value: string) => void }) => (
    <textarea aria-label="mock-editor" value={value} onChange={(e) => onChange(e.target.value)} />
  )
}));

const SUCCESS_RESPONSE: RunResponse = {
  ok: true,
  status: 'success',
  diagnostics: [],
  durationMs: 11,
  stdout: 'Hello TyC',
  stderr: '',
  astText: 'Program(...)',
  astJson: { kind: 'Program', fields: {} },
  stages: {
    parse: 'success',
    ast: 'success',
    semantic: 'success',
    codegen: 'success',
    assemble: 'success',
    run: 'success'
  }
};

describe('App', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('loads sample into editor and stdin', () => {
    render(<App />);

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Read integer' } });

    expect(screen.getByLabelText('mock-editor')).toHaveValue(
      'void main() {\n    int x = readInt();\n    printInt(x + 1);\n}'
    );
    expect(screen.getByPlaceholderText('Optional stdin input')).toHaveValue('41\n');
  });

  it('disables run button while running and enables after success', async () => {
    let release!: (value: typeof SUCCESS_RESPONSE) => void;
    const deferred = new Promise<typeof SUCCESS_RESPONSE>((resolve) => {
      release = resolve;
    });

    vi.spyOn(api, 'runProgram').mockReturnValue(deferred);

    render(<App />);
    const runButton = screen.getByRole('button', { name: 'Run' });

    fireEvent.click(runButton);
    expect(screen.getByRole('button', { name: 'Running...' })).toBeDisabled();

    release(SUCCESS_RESPONSE);
    await waitFor(() => expect(screen.getByRole('button', { name: 'Run' })).toBeEnabled());
  });

  it('renders success output', async () => {
    vi.spyOn(api, 'runProgram').mockResolvedValue(SUCCESS_RESPONSE);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Run' }));

    await screen.findByText('Hello TyC');
    expect(screen.getByText('success')).toBeInTheDocument();
  });

  it('shows AST tree view and allows switching to AST text', async () => {
    vi.spyOn(api, 'runProgram').mockResolvedValue(SUCCESS_RESPONSE);

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Run' }));
    await screen.findByText('Hello TyC');

    fireEvent.click(screen.getByRole('button', { name: 'AST' }));

    expect(screen.getByRole('button', { name: 'AST Tree' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'AST Text' })).toBeInTheDocument();
    expect(screen.queryByText('AST JSON')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'AST Text' }));
    expect(screen.getByText('Program(...)')).toBeInTheDocument();
  });

  it('renders timeout state and diagnostics', async () => {
    vi.spyOn(api, 'runProgram').mockResolvedValue({
      ...SUCCESS_RESPONSE,
      ok: false,
      status: 'timeout',
      diagnostics: [
        { stage: 'run', severity: 'error', message: 'Program exceeded 3 seconds.', line: null, column: null, raw: 'timeout' }
      ]
    });

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Run' }));

    await screen.findByText(/Program exceeded 3 seconds\./);
    expect(screen.getAllByText('timeout').length).toBeGreaterThan(0);
  });

  it('renders api_offline state when runner is unreachable', async () => {
    vi.spyOn(api, 'runProgram').mockRejectedValue(new TypeError('Failed to fetch'));

    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: 'Run' }));

    await screen.findByText('Cannot connect to runner API. Please check service availability.');
    expect(screen.getByText('api_offline')).toBeInTheDocument();
  });
});