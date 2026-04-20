"""
Test cases for TyC Static Semantic Checker
189 test cases covering all error types and comprehensive scenarios.
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
    """Test calling function before declaration raises UndeclaredFunction"""
    source = "void ping(int x) { pong(x - 1); } void pong(int x) { ping(x - 1); } void main() { ping(10); }"
    assert Checker(source).check_from_source() == "UndeclaredFunction(pong)"


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
    assert Checker(source).check_from_source() == "Redeclared(Variable, k)"


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
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(MemberAccess(Identifier(p).y))"


def test_036():
    source = "void func(UndefinedType p) {} void main() {}"
    assert "UndeclaredStruct" in Checker(source).check_from_source()


def test_037():
    source = "void main() { int result = calculate(); }"
    assert "UndeclaredFunction" in Checker(source).check_from_source()


def test_038():
    source = "void main() { for (int i = 0; i < 5; i++) {} i = 10; }"
    assert Checker(source).check_from_source() == 'Static checking passed'


def test_039():
    source = "void foo() {} void main() { foo(z); }"
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(z)"


def test_040():
    source = "struct A { int v; }; struct B { A a; }; void main() { B b; b.a.nonexistent = 10; }"
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(MemberAccess(MemberAccess(Identifier(b).a).nonexistent))"


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
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(a)"


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
    assert Checker(source).check_from_source() == "Static checking passed"


def test_049():
    source = "void main() { auto x; if (x > 5) {} }"
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BinaryOp(Identifier(x), >, IntLiteral(5)))"


def test_050():
    source = "void main() { auto x; auto y; y = x - 2; }"
    assert Checker(source).check_from_source() == "Static checking passed"


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
    assert Checker(source).check_from_source() == "Static checking passed"


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
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(a) = FloatLiteral(5.0))))"


def test_067():
    source = "void main() { string s = 5; }"
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(StringType(), s = IntLiteral(5)))"


def test_068():
    source = "float foo() { return 10; } void main() {}"
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ReturnStmt(return IntLiteral(10)))"


def test_069():
    source = "void main() { switch(1) { case 3.2: break; } }"
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(CaseStmt(case FloatLiteral(3.2): [BreakStmt()]))"


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
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(a) = FloatLiteral(5.5))))"


def test_085():
    source = "struct A{}; struct B{}; void main() { A a; B b; a = b; }"
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(a) = Identifier(b))))"


def test_086():
    source = "void foo(int a) {} void main() { string s; foo(s); }"
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(FuncCall(foo, [Identifier(s)]))"


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
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(MemberAccess(Identifier(a).v) = FloatLiteral(5.0))))"


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
    assert Checker(source).check_from_source() == "MustInLoop(ContinueStmt())"


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

def test_106():
    source = "int main(){auto a = {1,2};}"
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(VarDecl(auto, a = StructLiteral({IntLiteral(1), IntLiteral(2)})))"

def test_107():
    source = "void main() {int a = 5; int i = 5; for (int i = 0; i < 10; i++) {printInt(i);}}"
    assert Checker(source).check_from_source() == "Redeclared(Variable, i)"

def test_108():
    source = "void main() {int a = 1; switch(a){case 1: int a = 2; case 2: a = 3;}}"
    assert Checker(source).check_from_source() == "Static checking passed"

def test_109():
    source = """
    void incrementOperandError() {
        int x = 5;
        ++ x;
        x ++;
        ++5;                     // Error: TypeMismatchInExpression at unary operation (cannot increment literal)
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(PrefixOp(++IntLiteral(5)))"

def test_110():
    source = """
    void logicalError() {
        float f = 3.14;
        int x = !10;
    
        int not = !f;            // Error: TypeMismatchInExpression at unary operation
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(PrefixOp(!Identifier(f)))"

def test_111():
    source = """
    int foo() {
        auto a;
        auto b;
        a = b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(AssignExpr(Identifier(a) = Identifier(b)))"

def test_112():
    source = """
    foo() {
       return 1;
    }
    int foo1() {
       int a;
       a = foo();
       float b;
       b = foo();
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(b) = FuncCall(foo, []))))"

def test_113():
    source = """
    void main() {
        main();
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_114():
    source = """
    struct haha { haha x; };
    """
    assert Checker(source).check_from_source() == "UndeclaredStruct(haha)"

def test_115():
    source = """
    void main(){
    for (int i = 0; i < 10; i = i + 1) {
        int i = 2;
    }
    return;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_116():
    source = """
    void main(){
    for (int i = 0; i < 10; i = i + 1) {
        int i = 2;
    }
    int i = 5;
    return;
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, i)"


def test_117():
    source = """
    struct A { int a; int b;};
    void main(){
        A a = {1, 2};
        A b = a;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_118():
    source = """
    struct A { int a; int b;};
    void main(){
        B b = {1, 2};
    }
    """
    assert Checker(source).check_from_source() == "UndeclaredStruct(B)"

def test_119():
    source = """
    struct A { int a; int b;};
    void main(){
        auto a;
        auto b;
        A c = {a, b};
        auto d = a;
        auto e = b;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_120():
    source = """
    struct A { int x; int y; };
    void main() { int a; int b; auto c; c.x = a; }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(MemberAccess(Identifier(c).x))"

def test_121():
    source = """
    void main() { auto a = 1 + "abc"; }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(BinaryOp(IntLiteral(1), +, StringLiteral('abc')))"

def test_122():
    source = """
    void main() { auto x; int a = x + 1;}
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_123():
    source = """
    void main(){ int x = x + 1;}
    """
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(x)"

def test_124():
    source = """
    void main(){
        readInt();
        readFloat();
        readString();
        printInt(1);
        printFloat(1.0);
        printString("1");
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_125():
    source = """
    struct A { int a; string s;};
    void main(){
        int a = 0;
        int s = 1;
        A x;
        x = {a, s};
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(StructLiteral({Identifier(a), Identifier(s)}))"

def test_126():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t;};
    void main(){
        A x;
        B y;
        x = y;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(x) = Identifier(y))))"

def test_127():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        B x = {"a", "b", {1, 2.0}};
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(StructLiteral({StringLiteral('a'), StringLiteral('b'), StructLiteral({IntLiteral(1), FloatLiteral(2.0)})}))"

def test_128():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        B x;
        x = {"a", "b", {1, 2.0}};
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(StructLiteral({StringLiteral('a'), StringLiteral('b'), StructLiteral({IntLiteral(1), FloatLiteral(2.0)})}))"

def test_129():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        auto a; auto b; auto c; auto d;
        B x = {a, b, {c, d}};
        c = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(c) = FloatLiteral(2.0))))"

def test_130():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        auto a; auto b; auto c; auto d;
        B x = {a, b, {c, d}};
        a = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(a) = FloatLiteral(2.0))))"

def test_131():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        auto a; auto b; auto c; auto d;
        B x;
        x = {a, b, {c, d}};
        d = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(d) = FloatLiteral(2.0))))"

def test_132():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        auto a; auto b; auto c; auto d;
        B x;
        x = {a, b, {c, d}};
        b = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(b) = FloatLiteral(2.0))))"

def test_133():
    source = """
    struct A { int a; int b;};
    struct B { string s; string t; A a;};
    void main(){
        auto a; auto b; auto c; auto d;
        B x;
        x = {a, b, {c, d}};
        a = "Hello";
        b = "Portugal";
        c = 2;
        d = 2;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_134():
    source = """
    void main(){
        int a;
        float b;
        a = b = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(a) = AssignExpr(Identifier(b) = FloatLiteral(2.0)))))"

def test_135():
    source = """
    void main(){
        int a;
        int b;
        a = b = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(AssignExpr(Identifier(b) = FloatLiteral(2.0)))"

def test_136():
    source = """
    void main(){
        int a;
        int b;
        a = b = 2;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_137():
    source = """
    void main(){
        int a = 1;
        switch(x){
            case a: printString("Done"); break;
        }
    }
    """
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(x)"

def test_138():
    source = """
    void whileError() {
        int x = 10;
        string text = "hello";
        x = text;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(x) = Identifier(text))))"

def test_139():
    source = """
    void main(){
        int a;
        float b;
        a = (a = b);
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(AssignExpr(Identifier(a) = Identifier(b)))"

def test_140():
    source = """
    void main() {
        int a; int b;
        if (1) int a = b;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_141():
    source = """
    void main() {
        int a;
        switch (1) {
            case 1:
                int a;
                int b;
                float b;
        }
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, b)"

def test_142():
    source = """
    void main(int A, int B) {
        A = B;
        {
        int A;
        A = C;
        }
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, A)"

def test_143():
    source = """
    void main(){
        switch(1 || 2){case 1.0: }
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(CaseStmt(case FloatLiteral(1.0): []))"

def test_144():
    source = """
    void main() {
        auto a;
        int b = a + 1;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_145():
    source = """
    hehe(){
        int a = 1;
    }
    void main(){
        int a = hehe(); 
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(IntType(), a = FuncCall(hehe, [])))"

def test_146():
    source = """
    struct A { int a; float b; string c;};
    hehe(){
        return {1, 2.0, "3"};
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(ReturnStmt(return StructLiteral({IntLiteral(1), FloatLiteral(2.0), StringLiteral('3')})))"

def test_147():
    source = """
    void modulusError() {
        float f = 3.14;
        int x = 10 % 2;
    
        int result = f % x;      // Error: TypeMismatchInExpression at binary operation (float % int)
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(BinaryOp(Identifier(f), %, Identifier(x)))"
        
def test_148():
    source = """
    void main() {
        int a = +- 1;
        int b = +- 1.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(IntType(), b = PrefixOp(+PrefixOp(-FloatLiteral(1.0)))))"
    
def test_149():
    source = """
    void main() {
        auto a;
        auto b;
        int c = a + b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"

def test_150():
    source = """
    struct A{int A; float a;};
    struct B{int b; float b;};
    void main() {}
    """
    assert Checker(source).check_from_source() == "Redeclared(Member, b)"

def test_151():
    source = """
    void main() {
        auto b;
        int c = 1 + b;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_152():
    source = """
    void main() {
        auto b;
        int c = b > 2;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BinaryOp(Identifier(b), >, IntLiteral(2)))"

def test_153():
    source = """
    void main() {
        auto a;
        ! a;
        float b = a;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(FloatType(), b = Identifier(a)))"

def test_154():
    source = """
    void main() {
        auto a;
        a ++;
        float b = a;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(FloatType(), b = Identifier(a)))"


def test_155():
    source = """
    struct A {int a; int b;};
    struct B {int a; int c;};
    struct C {int b; int c;};

    void main(){
        auto x = {1, 2};
        {1,2}.b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(VarDecl(auto, x = StructLiteral({IntLiteral(1), IntLiteral(2)})))"

def test_156():
    source = """
    void main() {
        for(int a;;) break;
        int a;
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, a)"

def test_157():
    source = """
    void main() {
        int a = 5 == 3;
        int b = 5.0 > 3;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_158():
    source = """
    void main(){
        for (int a = 2.9; ; ) {}
    }
    """   
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(IntType(), a = FloatLiteral(2.9)))"


def test_159():
    source = """
    void switchError() {
        for (int i = 0; i < 5; ++i) {
            break;
            continue;
        }
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_160():
    source = """
    void main() {
        int a;
        switch (1) {
            case 1:
                int a;
                int b;
            case 2:
                int c = a;
                {int a;}
            default:
                int d = b;
                string b;
        }
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, b)"

        
def test_161():
    source = """
    void main() {
        int a;
    
        (a + 1) % 2;
        (a + 1.2) % 2;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(BinaryOp(BinaryOp(Identifier(a), +, FloatLiteral(1.2)), %, IntLiteral(2)))"
        
def test_162():
    source = """
    void main(int A, int B) {
        A = B;
        {
        int A;
        A = C;
        }
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, A)"

def test_163():
    source = """
    void main() {
        int A = A;
    }
    """
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(A)"
        
def test_164():
    source = """
    void main() {
        int a;
        switch (1) {
            case 1:
                int a;
                int b;
            case 2:
                float b;
        }
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, b)"

def test_165():
    source = """
    void main() {
        int a;
        while(1) int a;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_166():
    source = """
    void main() {
        int a; int b;
        if (1) int a = b;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed" 

def test_167():
    source = """
    void main() {
        int x = 10;
        int y = 3.14;
        int z = x + y;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(IntType(), y = FloatLiteral(3.14)))"

def test_168():
    source = """
    void main() {
        auto a;
        auto b;
        auto d = a % b;
        int c = a = b = d;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"
        

def test_169():
    source = """
    void main() {
        auto a;
        int b;
        auto c;
        a = b = c;
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"
        
def test_170():
    source = """
    int foo() {
        auto a;
        auto b;
        a = b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(AssignExpr(Identifier(a) = Identifier(b)))"

def test_171():
    source = """
    void foo(int a){}
    void main() {
        auto a;
        foo(a);
        float b = a;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(FloatType(), b = Identifier(a)))"
        
def test_172():
    source = """
    void main() {
        auto a;
        switch (a){}
        float b = a;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(VarDecl(FloatType(), b = Identifier(a)))"

def test_173():
    source = """
    func() { auto a; return a;}
    void main() {
        auto a = func();
        float b = a;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(ReturnStmt(return Identifier(a)))"
        
def test_174():
    source = """
    void unused_auto() {
        auto x;
    }  // TypeCannotBeInferred(BlockStmt([VarDecl(auto, x)]))
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BlockStmt([VarDecl(auto, x)]))"

def test_175():
    source = """
    void main(){
        int a = 1;
        {
            auto b;
            float c = 1.3;
            string d = "hl";
        }
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BlockStmt([VarDecl(auto, b), VarDecl(FloatType(), c = FloatLiteral(1.3)), VarDecl(StringType(), d = StringLiteral('hl'))]))"
        
def test_176():
    source = """
    void main(int a) {
        for(int a;;) return;
    }
    """
    assert Checker(source).check_from_source() == "Redeclared(Variable, a)"
        
def test_177():
    source = """
    void unused_auto() {
        switch (1) {
            case 1:
                auto c;
        }
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(SwitchStmt(switch IntLiteral(1) cases [CaseStmt(case IntLiteral(1): [VarDecl(auto, c)])]))"

def test_178():
    source = """
    void main() {
        switch (1) {
            case 1:
                break;
            case 2:
                break;
                for(;;) continue;
        }
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_179():
    source = """
    void main(){
        switch(1 || 2){case 1: int a; case 2: return 1;}
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ReturnStmt(return IntLiteral(1)))"

def test_180():
    source = """
    void main() {
        auto a; auto b;
        a = 1;
        a + b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"

def test_181():
    source = """
    void main() {
        auto x;
        int a = x + 1 + 2;
        x = 3.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(x) = FloatLiteral(3.0))))"

def test_182():
    source = """
    void main(){
        auto x;
        int a = 1 + x + 3;
        x = 2.0;
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(ExprStmt(AssignExpr(Identifier(x) = FloatLiteral(2.0))))"

def test_183():
    source = """
    void foo(int a, string b){}
    void main() {
        auto a;
        foo(a, a);
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(FuncCall(foo, [Identifier(a), Identifier(a)]))"

def test_184():
    source = """
    void main() {
        int a = 5;
        {
            auto a;
            auto b;
            b = 10;
        }
        float c = a + 3.1;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BlockStmt([VarDecl(auto, a), VarDecl(auto, b), ExprStmt(AssignExpr(Identifier(b) = IntLiteral(10)))]))"

def test_185():
    source = """
    void main() {
        auto a;
        switch (1){case a:}
        float b = a;
    }
    """
    # assert Checker(source).check_from_source() == "TypeMismatchInStatement(SwitchStmt(switch IntLiteral(1) cases [CaseStmt(case Identifier(a): [])]))"
    assert Checker(source).check_from_source() == "TypeMismatchInStatement(CaseStmt(case Identifier(a): []))"

def test_186():
    source = """
    void foo() {
        int x = 1;
        switch (x) {
            case - 1:
            case 1 + 2:
            case - 2:
            case 1 || 2 * 3 / 4 + 2:
        }
    }
    """
    assert Checker(source).check_from_source() == "Static checking passed"

def test_187():
    source = """
    void foo() {
        switch (1) {
            case x:
        }
    }
    """
    assert Checker(source).check_from_source() == "UndeclaredIdentifier(x)"

def test_188():
    source = """
    foo() {
        int a = foo();
        return 1;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(FuncCall(foo, []))"

def test_189():
    source = """
    struct Point {
        int x;
        int y;
    };
    
    void foo() {
        Point p = {10};
    }
    """
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(StructLiteral({IntLiteral(10)}))"

def test_190():
    source = """
    void main(){
    auto a; auto b;
        a=1;
        a+b;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"

def test_191():
    source = """
    void main() {
        auto a;
        a;
    }
    """
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(ExprStmt(Identifier(a)))"