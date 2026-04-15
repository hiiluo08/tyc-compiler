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
    assert "UndeclaredIdentifier" in Checker(source).check_from_source()


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
    assert "Static checking passed" in Checker(source).check_from_source()


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

def test_106():
    source = "int main(){auto a = {1,2};}"
    assert Checker(source).check_from_source() == "TypeCannotBeInferred(VarDecl(auto, a = StructLiteral({IntLiteral(1), IntLiteral(2)})))"

def test_107():
    source = "void main() {int a = 5; int i = 5; for (int i = 0; i < 10; i++) {printInt(i);}}"
    assert Checker(source).check_from_source() == "Redeclared(Variable, i)"

def test_108():
    source = "void main() {int a = 1; switch(a){case 1: int a = 2; case 2: a = 3;}}"
    assert Checker(source).check_from_source() == "Redeclared(Variable, a)"

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
    assert Checker(source).check_from_source() == "TypeMismatchInExpression(AssignExpr(Identifier(b) = FuncCall(foo, [])))"

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
    assert "Redeclared" in Checker(source).check_from_source()

def test_117():
    source = """
    void main(){
    main();
    }
    """
    assert "Static checking passed" in Checker(source).check_from_source()



# Test cases for TyC Static Semantic Checker

# This module contains test cases for the static semantic checker.
# 100 test cases covering all error types and comprehensive scenarios.
# """

# from tests.utils import Checker
# from src.utils.nodes import (
#     Program,
#     FuncDecl,
#     BlockStmt,
#     VarDecl,
#     AssignExpr,
#     ExprStmt,
#     IntType,
#     FloatType,
#     StringType,
#     VoidType,
#     StructType,
#     IntLiteral,
#     FloatLiteral,
#     StringLiteral,
#     Identifier,
#     BinaryOp,
#     MemberAccess,
#     FuncCall,
#     StructDecl,
#     MemberDecl,
#     Param,
#     ReturnStmt,
# )


# def run_tc_test(test_name: str, source: str, expected: str):
#     output = Checker(source).check_from_source()

#     assert output == expected, f"Output: {output}. Expected: {expected}"


# def test_001():
#     """Test a valid program that should pass all checks"""
#     source = """
#         void main() {
#             int x = 5;
#             int y = x + 1;
#         }
#     """
#     expected = "Static checking passed"
#     run_tc_test("001", source, expected)


# def test_002():
#     """Test valid program with auto type inference"""
#     source = """
#         void main() {
#             auto x = 10;
#             auto y = 3.14;
#             auto z = x + y;
#         }
#     """
#     expected = "Static checking passed"
#     run_tc_test("002", source, expected)


# def test_003():
#     """Test valid program with functions"""
#     source = """
#         int add(int x, int y) {
#             return x + y;
#         }
#         void main() {
#             int sum = add(5, 3);
#         }
#     """
#     expected = "Static checking passed"
#     run_tc_test("003", source, expected)


# def test_004():
#     """Test valid program with struct"""
#     source = """
#         struct Point {
#             int x;
#             int y;
#         };
#         void main() {
#             Point p;
#             p.x = 10;
#             p.y = 20;
#         }
#     """
#     expected = "Static checking passed"
#     run_tc_test("004", source, expected)


# def test_005():
#     """Test valid program with nested blocks"""
#     source = """
#         void main() {
#             int x = 10;
#             {
#                 int y = 20;
#                 int z = x + y;
#             }
#         }
#     """
#     expected = "Static checking passed"
#     run_tc_test("005", source, expected)

# def test_006():
#     source = """
#     struct Point {
#         int x;
#         int y;
#     };
#     struct Point {  // Redeclared(Struct, Point)
#         int z;
#     };
#     """
#     expected = "Redeclared(Struct, Point)"
#     run_tc_test("006", source, expected)

# def test_007():
#     source = """
#     int add(int x, int y) {
#         return x + y;
#     }
#     int add(int a, int b) {  // Redeclared(Function, add) - no function overloading
#         return a + b;
#     }
#     """
#     expected = "Redeclared(Function, add)"
#     run_tc_test("007", source, expected)

# def test_008():
#     source = """
#     struct foo {
#         int x;
#         int y;
#     };
#     int foo(int x, int y) {  // Not Redeclared: struct foo and function foo are distinct
#         return x + y;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("008", source, expected)

# def test_009():
#     source = """
#     void main() {
#         int count = 10;
#         int count = 20;  // Redeclared(Variable, count)
#     }
#     """
#     expected = "Redeclared(Variable, count)"
#     run_tc_test("009", source, expected)

# def test_010():
#     source = """
#     int calculate(int x, float y, int x) {  // Redeclared(Parameter, x)
#         return x + y;
#     }
#     """
#     expected = "Redeclared(Parameter, x)"
#     run_tc_test("010", source, expected)

# def test_011():
#     source = """
#     void func(int x) {
#         int x = 10;  // Redeclared(Variable, x)
#     }
#     """
#     expected = "Redeclared(Variable, x)"
#     run_tc_test("011", source, expected)

# def test_012():
#     source = """
#     struct Point {
#         int x;
#         int x;  // Redeclared(Member, x)
#     };
#     """
#     expected = "Redeclared(Member, x)"
#     run_tc_test("012", source, expected)

# def test_013():
#     source = """
#     void example() {
#         int value = 100;  // Function variable 
#         {
#             int value = 200;  // Valid: shadows function variable
#             {
#                 int value = 300;  // Valid: shadows block variable
#             }
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("013", source, expected)

# def test_014():
#     source = """
#     void test() {
#         int x = 10;
#         {
#             int y = 20;  // Valid: different variable name
#         }
#         int y = 30;  // Valid: y in outer scope doesn't conflict with y in inner scope (different block)
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("014", source, expected)

# def test_015():
#     source = """
#     struct Moi{};
#     Moi Moi(Moi Moi){Moi(Moi);} // if you wrong, you gay!
#     """
#     expected = "Static checking passed"
#     run_tc_test("015", source, expected)

# def test_016():
#     source = """
#     int main(){}
#     main(){}
#     """
#     expected = "Redeclared(Function, main)"
#     run_tc_test("016", source, expected)

# def test_017():
#     source = """
#     void readInt(){}
#     """
#     expected = "Redeclared(Function, readInt)"
#     run_tc_test("017", source, expected)

# def test_018():
#     source = """
#     struct UIA {};
#     UIA(){
#         UIA UIA;
#         if(1) UIA UIA;
#     }
#     """
#     expected = "Redeclared(Variable, UIA)"
#     run_tc_test("018", source, expected)

# def test_019():
#     source = """
#     struct UIA {};
#     UIA(){
#         UIA UIA;
#         if(1){ UIA UIA; }
#         else {UIA UIA; }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("019", source, expected)

# def test_020():
#     source = """
#     struct MOI {};

#     MOI MOI(){
#         MOI MOI;
#         for(MOI MOI;;){}
#     }
#     """
#     expected = "Redeclared(Variable, MOI)"
#     run_tc_test("020", source, expected)

# def test_021():
#     source = """
#     struct MEO{};
    
#     MEO cat(){
#         MEO moew;
#         for(;;) MEO moew;
#     }
#     """
#     expected = "Redeclared(Variable, moew)"
#     run_tc_test("021", source, expected)

# def test_022():
#     source = """
#     main(){
#         int uia;
#         for(;;){float uia;}
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("022", source, expected)

# def test_023():
#     source = """
#     m(){
#         int a;
#         switch(1){
#             case 1:
#                 int a;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("023", source, expected)

# def test_024():
#     source = """
#     m(){
#         switch(1){
#             case 1:
#                 int a;
#             case 2: 
#                 int a;
#         }
#     }
#     """
#     expected = "Redeclared(Variable, a)"
#     run_tc_test("024", source, expected)

# def test_025():
#     source = """
#     m(){
#         switch(1){
#             case 1:
#                 {int a;}
#             case 2: 
#                 int a;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("025", source, expected)

# def test_026():
#     source = """
#     m(int a){
#         {int a;}
#     }
#     """
#     expected = "Redeclared(Variable, a)"
#     run_tc_test("026", source, expected)

# def test_027():
#     source = """
#     m(int a){
#         {int b;}
#         int a;
#     }
#     """
#     expected = "Redeclared(Variable, a)"
#     run_tc_test("027", source, expected)

# def test_028():
#     source = """
#     m(){
#         int a;
#         {
#             int a;
#         }
#         int a;
#     }
#     """
#     expected = "Redeclared(Variable, a)"
#     run_tc_test("028", source, expected)

# def test_029():
#     source = """
#     m(){
#         {int a;} int a; {int a;}
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("029", source, expected)

# def test_030():
#     source = """
#     uia(){
#         int uia = u + i + a; 
#     }
#     """
#     expected = "UndeclaredIdentifier(u)"
#     run_tc_test("030", source, expected)

# def test_031():
#     source = """
#     void xy() {
#         int x = y + 5; 
#         int y = 10;
#     }
#     """
#     expected = "UndeclaredIdentifier(y)"
#     run_tc_test("031", source, expected)

# def test_032():
#     source = """
#     void method1() {
#         int localVar = 42;
#     }

#     void method2() {
#         int value = localVar + 1;  // UndeclaredIdentifier(localVar) - different function scope
#     }
#     """
#     expected = "UndeclaredIdentifier(localVar)"
#     run_tc_test("032", source, expected)

# def test_033():
#     source = """
#     void valid() {
#         int x = 10;
#         int y = x + 5;  // Valid: x is declared before use
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("033", source, expected)

# def test_034():
#     source = """
#     int calculate(int x, int y) {
#         int result = x + y;  // Valid: parameters x and y are visible
#         return result;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("034", source, expected)

# def test_035():
#     source = """
#     void nested() {
#         int outer = 10;
#         {
#             int inner = outer + 5;  // Valid: outer is in enclosing scope
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("035", source, expected)

# def test_036():
#     source = """
#     main(){
#         {int uia;}
#         int aiu = uia;
#     }
#     """
#     expected = "UndeclaredIdentifier(uia)"
#     run_tc_test("036", source, expected)

# def test_037():
#     source = """
#     m(){
#         int aiu;
#         {int aiu;}
#         int uia = aiu;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("037", source, expected)

# def test_038():
#     source = """
#     m(){
#         int a = a; // if you fail, you gay!
#     }
#     """
#     expected = "UndeclaredIdentifier(a)"
#     run_tc_test("038", source, expected)

# def test_039():
#     source = """
#     m(){
#         int a;
#         {
#             int b = a;
#             {
#                 int c = a;
#             }
#             { }
#             {
#                 int c = a;
#             }
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("039", source, expected)

# def test_040():
#     source = """
#     m(){
#         for(string i;;){}
#         i = "i luv u <3";
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("040", source, expected)

# def test_041():
#     source = """
#     m(){
#         for(;;) int uia;

#         { uia = 36; }    

#         for(;;) { int aiu; }

#         { aiu = 36; } 
#     }
#     """
#     expected = "UndeclaredIdentifier(aiu)"
#     run_tc_test("41", source, expected)

# def test_042():
#     source = """
#     m(){
#         int u;
#         int u = i;
#     }
#     """
#     expected = "Redeclared(Variable, u)"
#     run_tc_test("", source, expected)

# def test_043():
#     source = """
#     m(){
#         if(1) int i;
#         i = 1;
#         if(1) {int j;}
#         j = 1;
#     }
#     """
#     expected = "UndeclaredIdentifier(j)"
#     run_tc_test("043", source, expected)

# def test_044():
#     source = """
#     m(){
#         int x;
#         switch(1){
#             case 1: x = 1;
#         }
#         switch(2){
#             case 2: 
#                 int y;
#             default:
#                 y = 1;
#         }

#         switch(3){
#             case 3:
#                 {int z;}
#             default:
#                 z = 1;
#         }
#     }
#     """
#     expected = "UndeclaredIdentifier(z)"
#     run_tc_test("044", source, expected)

# def test_045():
#     source = """
#     m(){
#         uia();
#     }
#     """
#     expected = "UndeclaredFunction(uia)"
#     run_tc_test("045", source, expected)

# def test_046():
#     source = """
#     m(){
#       uia();
#     }
#     uia(){}
#     """
#     expected = "UndeclaredFunction(uia)"
#     run_tc_test("046", source, expected)

# def test_047():
#     source = """
#     uia(){}
#     m(){ uia(); }
#     """
#     expected = "Static checking passed"
#     run_tc_test("047", source, expected)

# def test_048():
#     source = """
#     void example() {
#         int x = readInt();       
#         printInt(x);             
#         float y = readFloat();  
#         printFloat(y);
#         string s = readString();  
#         printString(s);
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("048", source, expected)

# def test_049():
#     source = """
#     struct Moi{};
#     m(){Moi();}
#     """
#     expected = "UndeclaredFunction(Moi)"
#     run_tc_test("049", source, expected)

# def test_050():
#     source = """
#     m(){int Moi; Moi();}
#     """
#     expected = "UndeclaredFunction(Moi)"
#     run_tc_test("050", source, expected)

# def test_051():
#     source = """
#     void main() {
#         Point p;  
#     }

#     struct Point {
#         int x;
#         int y;
#     };
#     """
#     expected = "UndeclaredStruct(Point)"
#     run_tc_test("051", source, expected)

# def test_052():
#     source = """
#     struct Address {
#         string street;
#         City city;  
#     };

#     struct City {
#         string name;
#     };
#     """
#     expected = "UndeclaredStruct(City)"
#     run_tc_test("052", source, expected)

# def test_053():
#     source = """
#     struct Node{
#         int value;
#         Node next;
#     };
#     """
#     expected = "Static checking passed"
#     run_tc_test("053", source, expected)

# def test_054():
#     source = """
#     A(){
#         A a;
#     }
#     """
#     expected = "UndeclaredStruct(A)"
#     run_tc_test("054", source, expected)

# def test_055():
#     source = """
#     A A(){} // if you fail, you gay!
#     """
#     expected = "UndeclaredStruct(A)"
#     run_tc_test("055", source, expected)

# def test_056():
#     source = """
#     A(A A){}
#     """
#     expected = "UndeclaredStruct(A)"
#     run_tc_test("056", source, expected)

# def test_057():
#     source = """
#     m(){
#         auto a; auto i;
#         auto u = i + a;    
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(i), +, Identifier(a)))"
#     run_tc_test("057", source, expected)

# def test_058():
#     source = """
#     t() {
#         auto x;
#         auto y;
#         x = y;  
#     }
#     """
#     expected = "TypeCannotBeInferred(AssignExpr(Identifier(x) = Identifier(y)))"
#     run_tc_test("058", source, expected)

# def test_059():
#     source = """
#     t() {
#         auto x;
#         auto y;
#         int z = x < y;  
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(x), <, Identifier(y)))"
#     run_tc_test("059", source, expected)

# def test_060():
#     source = """
#     m() {
#         auto a;
#         auto b;
#         int c = a * b;
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), *, Identifier(b)))"
#     run_tc_test("060", source, expected)

# def test_061():
#     source = """
#     m() {
#         auto x;
#         auto y;  
#         auto z = x + "i love you"; 
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(x), +, StringLiteral('i love you')))"
#     run_tc_test("061", source, expected)

# def test_062():
#     source = """
#     m() {
#         auto x;
#     } 
#     """
#     expected = "TypeCannotBeInferred(BlockStmt([VarDecl(auto, x)]))"
#     run_tc_test("062", source, expected)

# def test_063():
#     source = """
#     func() {
#         auto x;
#         return x; 
#     }
#     """
#     expected = "TypeCannotBeInferred(ReturnStmt(return Identifier(x)))"
#     run_tc_test("063", source, expected)

# def test_064():
#     source = """
#     m() {
#         auto x = 10;   
#         auto y = 3.14;
#         auto msg = "luv u <3"; 
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("064", source, expected)

# def test_065():
#     source = """
#     m() {
#         auto a;
#         a = 10;      

#         auto b;
#         b = 3.14;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("065", source, expected)


# def test_066():
#     source = """
#     m() {
#         auto x;
#         x = readInt(); 

#         auto y;
#         int z = 10;
#         y = z + 5;  
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("066", source, expected)

# def test_067():
#     source = """
#     m() {
#         auto x;
#         auto y = x + 5;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("067", source, expected)

# def test_068():
#     source = """
#     m() {
#         int a = 10;
#         float b = 3.14;
#         auto c = a + b; 
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("068", source, expected)

# def test_069():
#     source = """
#     m() {
#         auto x;
#         printInt(x); 
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("069", source, expected)

# def test_070():
#     source = """
#     m(){
#         auto a;
#         int b = a;
#     }
#     """
#     expected = "TypeMismatchInStatement(VarDecl(IntType(), b = Identifier(a)))"
#     run_tc_test("070", source, expected)

# def test_071():
#     source = """
#     m(){
#         auto a = {"i luv u", 100}; // if u fail, u gay!
#     }
#     """
#     expected = "TypeCannotBeInferred(VarDecl(auto, a = StructLiteral({StringLiteral('i luv u'), IntLiteral(100)})))"
#     run_tc_test("071", source, expected)

# def test_072():
#     source = """
#     struct Moi{ int moi; };
#     m(){
#         Moi Moi;
#         auto moi = Moi;

#         auto m = moi.moi;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("072", source, expected)

# def test_073():
#     source = """
#     struct Moi{ int moi; };
#     Moi Moi(){}

#     moi(){
#         auto moi = Moi();
#         auto m = moi.moi;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("073", source, expected)

# def test_074():
#     source = """
#     struct Moi{ int moi; };
#     Moi Moi(Moi Moi){}

#     moi(){
#         auto Moi;
#         auto moi;
#         moi = Moi(Moi);
#         moi.moi = Moi.moi;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("074", source, expected)

# def test_075():
#     source = """
#     struct Uia { float uia; };
#     Uia Uia(){}
#     uia(){
#         auto Uia;
#         Uia = Uia();
#         return Uia;
#     }
#     UIA(){
#         auto uia = uia();
#         auto Uia = uia.uia;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("075", source, expected)

# def test_076():
#     source = """
#     m(){
#         auto a;
#         {
#             a = 5;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("076", source, expected)

# def test_077():
#     source = """
#     m(){
#         auto c;
#         {
#             float c;
#         }
#     }
#     """
#     expected = "TypeCannotBeInferred(BlockStmt([VarDecl(auto, c), BlockStmt([VarDecl(FloatType(), c)])]))"
#     run_tc_test("077", source, expected)

# def test_078():
#     source = """
#     struct Moew{};
#     moew(){
#         Moew Moew;
#         auto moew;
#         auto moe = moew + Moew;
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(moew), +, Identifier(Moew)))"
#     run_tc_test("078", source, expected)

# def test_079():
#     source = """
#     struct Moew{ int moew; };
#     moew(){
#         Moew Moew;
#         auto moew;
#         auto moe = moew + Moew.moew;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("079", source, expected)

# def test_080():
#     source = """
#     m(){
#         auto a = a;
#     }
#     """
#     expected = "UndeclaredIdentifier(a)"
#     run_tc_test("080", source, expected)

# def test_081():
#     source = """
#     m() {
#         int x = 5;
#         string text = "hello";
        
#         int sum = x + text;     
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(x), +, Identifier(text)))"
#     run_tc_test("081", source, expected)

# def test_082():
#     source = """
#     m() {
#         float f = 3.14;
#         int x = 10;
        
#         int result = f % x;    
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(f), %, Identifier(x)))"
#     run_tc_test("082", source, expected)

# def test_083():
#     source = """
#     m() {
#         int x = 10;
#         string text = "hello";
        
#         int result = x < text;
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(x), <, Identifier(text)))"
#     run_tc_test("083", source, expected)

# def test_084():
#     source = """
#     m() {
#         float f = 3.14;
#         int x = 10;
        
#         int result = f && x;     
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(f), &&, Identifier(x)))"
#     run_tc_test("084", source, expected)

# def test_085():
#     source = """
#     m() {
#         float f = 3.14;
#         ++f;                    
#         f++;
#     }
#     """
#     expected = "TypeMismatchInExpression(PrefixOp(++Identifier(f)))"
#     run_tc_test("085", source, expected)

# def test_086():
#     source = """
#     m() {
#         int x = 5; 
#         --(x + 1);             
#     }
#     """
#     expected = "TypeMismatchInExpression(PrefixOp(--BinaryOp(Identifier(x), +, IntLiteral(1))))"
#     run_tc_test("86", source, expected)

# def test_087():
#     source = """
#     m(){
#         1++;
#     }
#     """
#     expected = "TypeMismatchInExpression(PostfixOp(IntLiteral(1)++))"
#     run_tc_test("087", source, expected)

# def test_088():
#     source = """
#     struct Point{
#         int x; int y;
#     };
#     m(){
#         Point p = {1,2};
#         int z = p.z;
#     }
#     """
#     expected = "TypeMismatchInExpression(MemberAccess(Identifier(p).z))"
#     run_tc_test("088", source, expected)

# def test_089():
#     source = """
#     m(){
#         int z = 10;
#         int y = z.x;
#     }
#     """
#     expected = "TypeMismatchInExpression(MemberAccess(Identifier(z).x))"
#     run_tc_test("089", source, expected)

# def test_090():
#     source = """
#     m(){
#         printInt(1.2);
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(printInt, [FloatLiteral(1.2)]))"
#     run_tc_test("090", source, expected)

# def test_091():
#     source = """
#     m(int x, int y){}
#     n(){
#         m(1);
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(m, [IntLiteral(1)]))"
#     run_tc_test("091", source, expected)

# def test_092():
#     source = """
#     m(int x, int y){}
#     n(){
#         m(1, 2, 3);
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(m, [IntLiteral(1), IntLiteral(2), IntLiteral(3)]))"
#     run_tc_test("092", source, expected)

# def test_093():
#     source = """
#     m(){
#         int i = 1;
#         float j = 1.0;
#         int z = (i = j);
#     }
#     """
#     expected = "TypeMismatchInExpression(AssignExpr(Identifier(i) = Identifier(j)))"
#     run_tc_test("093", source, expected)

# def test_094():
#     source = """
#     struct Point {
#         int x;
#         int y;
#     };

#     m() {
#         int x = 10; int y = 20;
#         int sum = x + y;         
#         int compare = x < y;  
#         int logic = x && y;   
#         ++x;                     
        
        
#         Point p = {10, 20};
#         int x_coord = p.x;     
        
#         int a;
#         int b = (a = 5) + 7;      
        
#         int c; int d; int e;
#         c = d = e = 10;         
        
#         int result = (p.x = 15) + 5; 
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("094", source, expected)

# def test_095():
#     source = """
#     m(){
#         auto a;
#         auto b = a + 1.5;

#         auto c = b % a;
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(b), %, Identifier(a)))"
#     run_tc_test("095", source, expected)

# def test_096():
#     source = """
#     struct Point { int x; int y;};

#     Point Point(int x, int y){
#         return {x, y}; // if you fail, you gay
#     }
#     m(){
#         Point p = {1, 2};
#         auto point = Point(p.x, p.y);
#         auto i = point.x % point.y;
#         auto j = !i;
#         auto z = Point(i, j).x;
#         int t = z % 5;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("096", source, expected)

# def test_097():
#     source = """
#     struct Node{
#         int value;
#         Node next;
#     };
#     // if you fail, you gay
#     Node(int value){
#         Node null;
#         Node node = {value, null};
#         return node;
#     }

#     it(Node node){
#         return node.value;
#     }

#     m(){
#         int x;
#         Node head = Node(x);
#         auto node = head.next;
#         Node dummy = Node(node.value);

#         int value = it({x, {head.value, {node.value, dummy}}});
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("097", source, expected)

# def test_098():
#     source = """
#     struct Node{
#         int value;
#         Node next;
#     };
#     // if you fail, you gay
#     Node(int value){
#         Node null;
#         return {value, null};
#     }
#     """
#     expected = "TypeMismatchInStatement(ReturnStmt(return StructLiteral({Identifier(value), Identifier(null)})))"
#     run_tc_test("098", source, expected)

# def test_099():
#     source = """
#     struct A{};
#     struct B{};

#     m(){
#         A a;
#         B b = a;
#     }
#     """
#     expected = "TypeMismatchInStatement(VarDecl(StructType(B), b = Identifier(a)))"
#     run_tc_test("099", source, expected)

# def test_100():
#     source = """
#     struct A{};
#     struct B{};

#     m(){
#         A a;
#         B b ;
#         b = a;
#     }
#     """
#     expected = "TypeMismatchInExpression(AssignExpr(Identifier(b) = Identifier(a)))"
#     run_tc_test("100", source, expected)

# def test_101():
#     source = """
#     struct A{};
#     struct B{};

#     m(A a){}

#     n(){
#         B b;
#         m(b);
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(m, [Identifier(b)]))"
#     run_tc_test("101", source, expected)

# def test_102():
#     source = """
#     struct A{};
#     m(A a){}

#     n(){
#         m({});
#         m(1);
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(m, [IntLiteral(1)]))"
#     run_tc_test("102", source, expected)

# def test_103():
#     source = """
#     struct A{int a; int b;};
#     struct B{string s; A a;};
#     struct C{ A a; B b; };

#     m(C C){}

#     n(){
#         m({{1, 2}, {"uia", {3, 4}}});
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("103", source, expected)

# def test_104():
#     source = """
#     main(int m){
#         m = 1.2;
#     }
#     """
#     expected = "TypeMismatchInExpression(AssignExpr(Identifier(m) = FloatLiteral(1.2)))"
#     run_tc_test("104", source, expected)

# def test_105():
#     source = """
#     n(){}

#     m(){
#         auto a = n();
#     }
#     """
#     expected = "TypeCannotBeInferred(VarDecl(auto, a = FuncCall(n, [])))"
#     run_tc_test("105", source, expected)

# def test_106():
#     source = """
#     n(){}

#     m(){
#         auto a;
#         auto b = a + n();
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), +, FuncCall(n, [])))"
#     run_tc_test("106", source, expected)

# def test_107():
#     source = """
#     n(){}

#     m(){
#         auto a;
#         auto b;
#         b = a + n();
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), +, FuncCall(n, [])))"
#     run_tc_test("107", source, expected)

# def test_108():
#     source = """
#     n(){}
#     m(int a){
#         m(n());
#     }
#     """
#     expected = "TypeMismatchInExpression(FuncCall(m, [FuncCall(n, [])]))"
#     run_tc_test("108", source, expected)

# def test_109():
#     source = """
#     struct Node{
#         int value;
#         Node next;
#     };
#     m(){
#         Node p;
#         int v = p.next.next.value;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("109", source, expected)

# def test_110():
#     source = """
#     m(){
#         int x;
#         if(1){}
#         while(x){}
#         for(;x+1;){}
#         switch(x%2){case x*2: {}}
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("110", source, expected)

# def test_111():
#     source = """
#     m(){
#         float x;
#         if(x){}
#     }
#     """
#     expected = "TypeMismatchInStatement(IfStmt(if Identifier(x) then BlockStmt([])))"
#     run_tc_test("111", source, expected)

# def test_112():
#     source = """
#     int a(){
#         return "i love you";
#     }
#     """
#     expected = "TypeMismatchInStatement(ReturnStmt(return StringLiteral('i love you')))"
#     run_tc_test("112", source, expected)

# def test_113():
#     source = """
#     void a(){
#         return "i luv u";
#     }
#     """
#     expected = "TypeMismatchInStatement(ReturnStmt(return StringLiteral('i luv u')))"
#     run_tc_test("113", source, expected)

# def test_114():
#     source = """
#     string a(){
#         return;
#     }
#     """
#     expected = "TypeMismatchInStatement(ReturnStmt(return))"
#     run_tc_test("114", source, expected)

# def test_115():
#     source = """
#     struct Point{
#         int x;
#         int y;
#     };
#     m(){
#         int x;
#         int y;
#         if(x > y){
#             for(x = 5; x == y; x++){
#                 while(y++){
#                     switch(readInt()){
#                         case x * y: {}
#                         case x - y: {}
#                     }
#                 }
#             }
#             Point p1 = {x, y};
#             Point p2 = {y, x};
#             p2.x = (p1.y = 1) + 2;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("115", source, expected)

# def test_116():
#     source = """
#     int m(){
#         auto a;
#         return a;
#     }

#     """
#     expected = "TypeCannotBeInferred(ReturnStmt(return Identifier(a)))"
#     run_tc_test("116", source, expected)

# # 117 đến 121, có thể fail
# def test_117():
#     source = """
#     m(){
#         auto a;
#         if(a){};
#     }
#     """
#     expected = "TypeCannotBeInferred(IfStmt(if Identifier(a) then ExprStmt(StructLiteral({}))))"
#     run_tc_test("117", source, expected)

# def test_118():
#     source = """
#     m(){
#         auto a;
#         while(a){}
#     }
#     """
#     expected = "TypeCannotBeInferred(WhileStmt(while Identifier(a) do BlockStmt([])))"
#     run_tc_test("118", source, expected)

# def test_119():
#     source = """
#     m(){
#         auto a;
#         for(;a;){}
#     }
#     """
#     expected = "TypeCannotBeInferred(ForStmt(for None; Identifier(a); None do BlockStmt([])))"
#     run_tc_test("119", source, expected)

# def test_120():
#     source = """
#     m(){
#         auto a;
#         switch(a){}
#     }
#     """
#     expected = "TypeCannotBeInferred(SwitchStmt(switch Identifier(a) cases []))"
#     run_tc_test("120", source, expected)

# def test_121():
#     source = """
#     m(){
#         auto a;
#         switch(1){
#             case a: {}
#         }
#     }
#     """
#     expected = "TypeCannotBeInferred(CaseStmt(case Identifier(a): [BlockStmt([])]))"
#     run_tc_test("121", source, expected)

# def test_122():
#     source = """
#     m(){
#         int n;
#         for(int n;;){}
#     }
#     """
#     expected = "Redeclared(Variable, n)"
#     run_tc_test("122", source, expected)

# def test_123():
#     source = """
#     m(){
#         int n;
#         switch(1){
#             case n * 2:
#                 int n;
#                 int m;
#             case m * 3:
#                 int m;
            
#         }
#     }
#     """
#     expected = "Redeclared(Variable, m)"
#     run_tc_test("123", source, expected)

# def test_124():
#     source = """
#     n(){
#         return n();
#     }   
#     """
#     expected = "TypeCannotBeInferred(ReturnStmt(return FuncCall(n, [])))"
#     run_tc_test("124", source, expected)

# def test_124():
#     source = """
#     n(int x){
#         if(x == 3) return x;
#         else return "i luv u";
#     }
#     """
#     expected = "TypeMismatchInStatement(ReturnStmt(return StringLiteral('i luv u')))"
#     run_tc_test("124", source, expected)

# def test_125():
#     source = """
#     f(int n){
#         if(n <= 1) return 1;
#         return f(n - 1) + f(n - 2);
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("125", source, expected)

# def test_126():
#     source = """
#     m(){
#         {
#             for(int m;;){}
#         }
#         printInt(m);
#     }
#     """
#     expected = "UndeclaredIdentifier(m)"
#     run_tc_test("126", source, expected)

# def test_127():
#     source = """
#     int n(float x){}
#     m(){
#         for(auto a; n(a); a++){
#             int z = a % 5;
#         }
#     }
#     """
#     expected = "TypeMismatchInExpression(PostfixOp(Identifier(a)++))"
#     run_tc_test("127", source, expected)

# def test_128():
#     source = """
#     int n(float x){}
#     m(){
#         for(auto a; n(a);){
#             int z = a % 5;
#         }
#     }
#     """
#     expected = "TypeMismatchInExpression(BinaryOp(Identifier(a), %, IntLiteral(5)))"
#     run_tc_test("128", source, expected)

# # test nay co the mismatch o ++
# def test_129():
#     source = """
#     m(){
#         for(auto a;;a++){}
#     }
#     """
#     expected = "TypeCannotBeInferred(PostfixOp(Identifier(a)++))"
#     run_tc_test("129", source, expected)

# # test nay co the mismatch o !
# def test_130():
#     source = """
#     m(){
#         auto a;
#         if(!a){}
#     }
#     """
#     expected = "TypeCannotBeInferred(PrefixOp(!Identifier(a)))"
#     run_tc_test("130", source, expected)

# def test_131():
#     source = """
#     m(){}
#     n(){
#         if(m()){}    
#     }
#     """
#     expected = "TypeMismatchInStatement(IfStmt(if FuncCall(m, []) then BlockStmt([])))"
#     run_tc_test("131", source, expected)

# def test_132():
#     source = """
#     m(){}
#     n(){
#         switch(++m()){}
#     }
#     """
#     expected = "TypeMismatchInExpression(PrefixOp(++FuncCall(m, [])))"
#     run_tc_test("132", source, expected)

# # test nay co the mismatch o literal
# def test_133():
#     source = """
#     struct Point{ int x; int y;};
#     m(){
#         auto a;
#         Point p = {a, 1};
#         int b = a;
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("133", source, expected)

# def test_134():
#     source = """
#     m(){
#         auto a;
#         auto b;
#         auto c = (a + b) + 1;
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"
#     run_tc_test("134", source, expected)

# def test_135():
#     source = """
#     m(){
#         auto a;
#         auto b;
#         auto c;
#         c = (a + b) + 1;
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"
#     run_tc_test("135", source, expected)

# def test_136():
#     source = """
#     n(int a){}

#     m(){
#         auto a;
#         auto b;
#         n(a+b);
#     }
#     """
#     expected = "TypeCannotBeInferred(BinaryOp(Identifier(a), +, Identifier(b)))"
#     run_tc_test("136", source, expected)

# def test_137():
#     source = """
#     n(int a){}

#     m(){
#         auto a;
#         auto b;
#         n(a);
#         n(b);
#         n(a+b);
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("137", source, expected)

# def test_138():
#     source = """
#     m(){
#         break;
#         continue;
#     }
#     """
#     expected = "MustInLoop(break)"
#     run_tc_test("138", source, expected)

# def test_139():
#     source = """
#     m(){
#         if(1){
#             break;
#             continue;
#         }
#     }
#     """
#     expected = "MustInLoop(break)"
#     run_tc_test("139", source, expected)

# def test_140():
#     source = """
#     m(){
#         int x = 1;
#         switch(x){
#             case 1:
#                 break;
#                 continue;
#         }
#     }
#     """
#     expected = "MustInLoop(continue)"
#     run_tc_test("140", source, expected)

# def test_141():
#     source = """
#     m(int n){
#         for(int i = 2; i <= n / 2; i++){
#             if(n % 2 == 0) break;
#             else continue;
#         }
#         int j = 2;
#         while(j <= n /2){
#             if(n % 3 == 1) continue;
#             else break;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("141", source, expected)

# def test_142():
#     source = """
#     m(){
#         switch(1){
#             case 1:
#                 printInt(1);
#                 break;
#             case 2:
#             case 3:
#                 break;
#             default:
#                 printString("i l u");
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("142", source, expected)

# def test_142():
#     source = """
#     m(){
#         for(int i;;){
#             for(int j;;){
#                 if(j) break;
#                 else continue;
#             }
#             if(i) break;
#             continue;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("142", source, expected)

# def test_143():
#     source = """
#     m(){
#         for(;;) break;

#         for(;;) continue;

#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("143", source, expected)

# def test_144():
#     source = """
#     m(){
#         for(;;) break;
#         continue;
#     }
#     """
#     expected = "MustInLoop(continue)"
#     run_tc_test("144", source, expected)

# def test_145():
#     source = """
#     m(){
#         for(;;){
#             switch(1){
#                 case 1:
#                     continue;
#             }
#             break;
#         }
#     }
#     """
#     expected = "Static checking passed"
#     run_tc_test("145", source, expected)

# def test_146():
#     source = """
#     m(){
#         switch(1){}

#         break;
#     }
#     """
#     expected = "MustInLoop(break)"
#     run_tc_test("146", source, expected)