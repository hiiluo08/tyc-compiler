import type { Sample } from './types';

export const samples: Sample[] = [
  {
    name: 'Hello TyC',
    source: `void main() {\n    printString("Hello TyC");\n}`,
    stdin: ''
  },
  {
    name: 'Read integer',
    source: `void main() {\n    int x = readInt();\n    printInt(x + 1);\n}`,
    stdin: '41\n'
  },
  {
    name: 'Syntax error',
    source: `void main( {\n}`,
    stdin: ''
  },
  {
    name: 'Semantic error',
    source: `void main() {\n    int x = "abc";\n}`,
    stdin: ''
  },
  {
    name: 'Timeout',
    source: `void main() {\n    while (1) {}\n}`,
    stdin: ''
  }
];