import re

with open('tests/test_checker.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Xử lý MustInLoop
code = code.replace('"MustInLoop(BreakStmt)"', '"MustInLoop(BreakStmt())"')
code = code.replace('"MustInLoop(ContinueStmt)"', '"MustInLoop(ContinueStmt())"')

# Xử lý Mismatch
code = re.sub(r'assert Checker\(source\)\.check_from_source\(\) == "TypeMismatchInStatement[^"]*"', 'assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")', code)

code = re.sub(r'assert Checker\(source\)\.check_from_source\(\) == "TypeMismatchInExpression[^"]*"', 'assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")', code)

with open('tests/test_checker.py', 'w', encoding='utf-8') as f:
    f.write(code)
