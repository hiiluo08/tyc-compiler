"""
Test cases for TyC Static Semantic Checker
105 test cases covering all error types and comprehensive scenarios.
"""
from tests.utils import Checker


# ============================================================================
# Group 1: Valid Programs (test_001 - test_015)
# ============================================================================

def test_001():
    """Test standard simple variable declarations"""
    source = "void main() { int x = 5; int y = x + 1; }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_002():
    """Test auto type inference with init value"""
    source = "void main() { auto x = 10; auto y = 3.14; auto z = x + 5; }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_003():
    """Test simple functions and forward declarations"""
    source = "int add(int x, int y) { return x + y; } void main() { int s = add(5, 3); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_004():
    """Test struct initialization and member access"""
    source = "struct Point { int x; int y; }; void main() { Point p; p.x = 10; p.y = 20; }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_005():
    """Test nested blocks and variable shadowing"""
    source = "void main() { int x = 10; { int x = 20; { int x = 30; } int z = x + 1; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_006():
    """Test recursive function"""
    source = "int fact(int n) { if (n == 0) return 1; return n * fact(n - 1); } void main() { fact(5); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_007():
    """Test mutually recursive functions - functions have global scope, visible everywhere"""
    source = "void ping(int x) { pong(x - 1); } void pong(int x) { ping(x - 1); } void main() { ping(10); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_008():
    """Test auto inference from function return value"""
    source = "int get_num() { return 42; } void main() { auto x = get_num(); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_009():
    """Test complex operations and boolean-like ints"""
    source = "void main() { int x = 0; if (x == 0 && x != 1 || x > 2) { x = 1; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_010():
    """Test while loop with break and continue"""
    source = "void main() { int i = 0; while (i < 10) { i++; if (i == 5) continue; if (i == 9) break; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_011():
    """Test for loop block scoping"""
    source = "void main() { for (int i = 0; i < 10; i++) { int x = i; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_012():
    """Test switch statement"""
    source = "void main() { int x = 2; switch (x) { case 1: break; case 2: break; default: break; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_013():
    """Test % modulo operator forcing inference"""
    source = "void main() { auto x; auto y = x % 5; }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_014():
    """Test return statement void and types"""
    source = "void foo() { return; } int bar() { return 5; } void main() { foo(); int x = bar(); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_015():
    """Test multiple structs and member scopes"""
    source = "struct A { int v; }; struct B { A a; }; void main() { B b; b.a.v = 10; }"
    assert Checker(source).check_from_source() == "Static checking passed"


# ============================================================================
# Group 2: Redeclared Errors (test_016 - test_030)
# ============================================================================

def test_016():
    source = "void main() { int x = 5; float x = 3.14; }"
    assert "Redeclared" in Checker(source).check_from_source()


def test_017():
    source = "void foo() {} void foo() {} void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_018():
    source = "struct Point {}; struct Point {}; void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_019():
    source = "void foo(int a, float a) {} void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_020():
    source = "struct A { int v; float v; }; void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_021():
    source = "void main() { for (int i = 0; i < 5; i++) { int i = 10; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_022():
    source = "void main() { { int blockVar = 1; int blockVar = 2; } }"
    assert "Redeclared" in Checker(source).check_from_source()


def test_023():
    source = "void calc(int param) { int param = 5; } void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_024():
    source = "void main() { int a; { float a; float a; } }"
    assert "Redeclared" in Checker(source).check_from_source()


def test_025():
    source = "struct Config { int path; float path; }; void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_026():
    source = "void draw(int x, int y, int x) {} void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_027():
    source = "void main() { auto z = 1; auto z = 2; }"
    assert "Redeclared" in Checker(source).check_from_source()


def test_028():
    source = "void main() { for(int k=0; k<1; k++) {} for(int k=0; k<2; k++) { int k; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_029():
    source = "void start() {} void get() {} void start() {} void main() {}"
    assert "Redeclared" in Checker(source).check_from_source()


def test_030():
    source = "void main() { int b; if (1) { int b; int b; } }"
    assert "Redeclared" in Checker(source).check_from_source()


# ============================================================================
# Group 3: Undeclared Errors (test_031 - test_045)
# ============================================================================

def test_031():
    source = "void main() { int x = y + 5; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_032():
    source = "void main() { int x = 5; { int y = 10; } x = y; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_033():
    source = "void main() { run(); }"
    assert "UndeclaredFunction" in Checker(source).check_from_source()


def test_034():
    source = "struct Point { int x; }; void main() { Rect r; }"
    assert "UndeclaredStruct" in Checker(source).check_from_source()


def test_035():
    source = "struct Point { int x; }; void main() { Point p; p.y = 10; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_036():
    source = "void func(UndefinedType p) {} void main() {}"
    assert "UndeclaredStruct" in Checker(source).check_from_source()


def test_037():
    source = "void main() { int result = calculate(); }"
    assert "UndeclaredFunction" in Checker(source).check_from_source()


def test_038():
    source = "void main() { for (int i = 0; i < 5; i++) {} i = 10; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_039():
    source = "void foo() {} void main() { foo(z); }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_040():
    source = "struct A { int v; }; struct B { A a; }; void main() { B b; b.a.nonexistent = 10; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_041():
    source = "struct A { UndefinedStruct b; }; void main() {}"
    assert "UndeclaredStruct" in Checker(source).check_from_source()


def test_042():
    source = "void main() { auto x = unknown_variable; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_043():
    source = "void foo() { x = 5; int x = 10; } void main() {}"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_044():
    source = "void main() { Point p; }"
    assert "UndeclaredStruct" in Checker(source).check_from_source()


def test_045():
    source = "void foo() { if(1) int a; a = 5; } void main() {}"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


# ============================================================================
# Group 4: TypeCannotBeInferred Errors (test_046 - test_055)
# ============================================================================

def test_046():
    source = "void main() { auto x; auto y = x; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_047():
    source = "void main() { auto a; auto b; a = b; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_048():
    source = "void main() { auto x; auto y = x + 5; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_049():
    source = "void main() { auto x; if (x > 5) {} }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_050():
    source = "void main() { auto x; auto y; y = x - 2; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_051():
    source = "void main() { auto x; auto y; auto z = x + y; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_052():
    source = "void main() { auto val; auto res = +val; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_053():
    source = "void main() { auto x; auto y = x * 2.5; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_054():
    source = "void main() { auto obj; int val = obj.member; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


def test_055():
    source = "void main() { auto x; int y = x / 2; }"
    assert "TypeCannotBeInferred" in Checker(source).check_from_source()


# ============================================================================
# Group 5: TypeMismatchInStatement Errors (test_056 - test_080)
# ============================================================================

def test_056():
    source = "void main() { int x = 3.14; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_057():
    source = "void main() { float y = 5; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_058():
    source = "void main() { if (3.14) { int x = 1; } }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_059():
    source = "void main() { while (\"hello\") { int x = 1; } }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_060():
    source = "void main() { for(int i=0; 3.5; i++) {} }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_061():
    source = "void main() { switch(3.14) { case 1: break; } }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_062():
    source = "int add() { return 3.14; } void main() {}"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_063():
    source = "void foo() { return 10; } void main() {}"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_064():
    source = "int get_num() { return; } void main() {}"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_065():
    source = "struct Item{}; struct Box{}; void main() { Item item; Box box = item; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_066():
    source = "void main() { int a; a = 5.0; }"  
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_067():
    source = "void main() { string s = 5; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_068():
    source = "float foo() { return 10; } void main() {}"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_069():
    source = "void main() { switch(1) { case 3.2: break; } }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_070():
    source = "void main() { int x; for(x=0; x<10; ++x) {} }" 
    assert Checker(source).check_from_source() == "Static checking passed"


def test_071():
    source = "void main() { if (1) return 1; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_072():
    source = "void bar() { if(1>0) { return 0; } } void main() {}"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_073():
    source = "struct A{}; void main() { int x = A; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_074():
    source = "void main() { int x = \"string\"; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_075():
    source = "void main() { if (1 + 2) { } else if (\"err\") { } }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


# ============================================================================
# Group 6: TypeMismatchInExpression Errors (test_076 - test_095)
# ============================================================================

def test_076():
    source = "void main() { int x = 5 + \"str\"; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_077():
    source = "void main() { float x = 3.14 % 2; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_078():
    source = "void main() { int x = 1 && 2.5; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_079():
    source = "void main() { int x = !3.14; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_080():
    source = "void main() { string s = \"str\"; s++; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_081():
    source = "void main() { int arg = 5; int x = arg.v; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_082():
    source = "void foo(int a, float b) {} void main() { foo(1, 2); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_083():
    source = "void foo(int a) {} void main() { foo(1, 2); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_084():
    source = "void main() { int a; a = 5.5; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_085():
    source = "struct A{}; struct B{}; void main() { A a; B b; a = b; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_086():
    source = "void foo(int a) {} void main() { string s; foo(s); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_087():
    source = "void main() { int x = 1 > \"string\"; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_088():
    source = "void main() { float x = 5.0; float y = -\"str\"; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_089():
    source = "void main() { int x = 1; int y = x || 5.0; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_090():
    source = "struct A { int v; }; void main() { A a; a.v = 5.0; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_091():
    source = "void main() { float a; float b = ++a; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_092():
    source = "void main() { float a; float b = a--; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_093():
    source = "void foo(int a, float b) {} void main() { foo(1.5, 2.5); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_094():
    source = "struct Car {}; void main() { int x = Car; }"
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


def test_095():
    source = "void main() { float x = 3.14; int y = x == \"str\"; }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


# ============================================================================
# Group 7: MustInLoop Errors / Edge Cases (test_096 - test_105)
# ============================================================================

def test_096():
    source = "void main() { break; }"
    assert Checker(source).check_from_source() == "MustInLoop(BreakStmt())"


def test_097():
    source = "void main() { continue; }"
    assert Checker(source).check_from_source() == "MustInLoop(ContinueStmt())"


def test_098():
    source = "void main() { if (1) { break; } }"
    assert Checker(source).check_from_source() == "MustInLoop(BreakStmt())"


def test_099():
    source = "void main() { switch(1) { case 1: continue; } }"
    assert Checker(source).check_from_source() == "MustInLoop(ContinueStmt())"


def test_100():
    source = "void main() { int i = 0; while(i<10) { switch(i) { case 1: break; case 2: continue; } } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_101():
    source = "void main() { for(int i=0; i<10; i++) { if (i == 5) continue; } }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_102():
    # Calling global built-ins
    source = "void main() { int x = readInt(); printFloat(3.14); }"
    assert Checker(source).check_from_source() == "Static checking passed"


def test_103():
    source = "void main() { float f = readString(); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInStatement")


def test_104():
    source = "void main() { printInt(3.14); }"
    assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")


def test_105():
    source = "void main() { int a; { { { break; } } } }"
    assert Checker(source).check_from_source() == "MustInLoop(BreakStmt())"
