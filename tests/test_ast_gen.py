"""
AST Generation test cases for TyC compiler.
"""

import pytest
from tests.utils import ASTGenerator
from src.utils.nodes import *

# ============================================================================
# 1. Program Structure & Functions
# ============================================================================

def test_001():
    source = 'void main() {}'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_002():
    source = 'int main() { return 0; }'
    expected = Program([
        FuncDecl(IntType(), "main", [], BlockStmt([
            ReturnStmt(IntLiteral(0))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_003():
    source = 'main() {}'
    expected = Program([
        FuncDecl(None, "main", [], BlockStmt([]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_004():
    source = 'void foo(int x) {}'
    expected = Program([
        FuncDecl(VoidType(), "foo", [Param(IntType(), "x")], BlockStmt([]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_005():
    source = 'void bar(float y, string z) {}'
    expected = Program([
        FuncDecl(VoidType(), "bar", [Param(FloatType(), "y"), Param(StringType(), "z")], BlockStmt([]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 2. Variable Declarations
# ============================================================================

def test_006():
    source = 'void main() { int x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(IntType(), "x")
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_007():
    source = 'void main() { int x = 10; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(IntType(), "x", IntLiteral(10))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_008():
    source = 'void main() { auto x = 10; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", IntLiteral(10))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_009():
    source = 'void main() { auto y; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "y")
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_010():
    source = 'void main() { float f = 1.5; string s = "hello"; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(FloatType(), "f", FloatLiteral(1.5)),
            VarDecl(StringType(), "s", StringLiteral("hello"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 3. Struct Declarations
# ============================================================================

def test_011():
    source = 'struct A {};'
    expected = Program([
        StructDecl("A", [])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_012():
    source = 'struct Point { int x; int y; };'
    expected = Program([
        StructDecl("Point", [
            MemberDecl(IntType(), "x"),
            MemberDecl(IntType(), "y")
        ])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_013():
    source = 'struct Person { string name; int age; float height; };'
    expected = Program([
        StructDecl("Person", [
            MemberDecl(StringType(), "name"),
            MemberDecl(IntType(), "age"),
            MemberDecl(FloatType(), "height")
        ])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_014():
    source = 'struct Rect { Point p1; Point p2; };'
    expected = Program([
        StructDecl("Rect", [
            MemberDecl(StructType("Point"), "p1"),
            MemberDecl(StructType("Point"), "p2")
        ])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 4. Expressions - Arithmetic
# ============================================================================

def test_015():
    source = 'void main() { auto x = 1 + 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "+", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_016():
    source = 'void main() { auto x = 1 - 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "-", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_017():
    source = 'void main() { auto x = 1 * 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "*", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_018():
    source = 'void main() { auto x = 1 / 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "/", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_019():
    source = 'void main() { auto x = 1 % 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "%", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_020():
    source = 'void main() { auto x = 1 + 2 * 3; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "+", BinaryOp(IntLiteral(2), "*", IntLiteral(3))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_021():
    source = 'void main() { auto x = (1 + 2) * 3; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(BinaryOp(IntLiteral(1), "+", IntLiteral(2)), "*", IntLiteral(3)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 5. Expressions - Relational & Logical
# ============================================================================

def test_022():
    source = 'void main() { auto x = 1 < 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "<", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_023():
    source = 'void main() { auto x = 1 <= 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "<=", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_024():
    source = 'void main() { auto x = 1 > 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), ">", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_025():
    source = 'void main() { auto x = 1 >= 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), ">=", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_026():
    source = 'void main() { auto x = 1 == 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "==", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_027():
    source = 'void main() { auto x = 1 != 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "!=", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_028():
    source = 'void main() { auto x = 1 && 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "&&", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_029():
    source = 'void main() { auto x = 1 || 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(IntLiteral(1), "||", IntLiteral(2)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_030():
    source = 'void main() { auto x = !1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", PrefixOp("!", IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 6. Expressions - Unary & Postfix
# ============================================================================

def test_031():
    source = 'void main() { auto x = -1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", PrefixOp("-", IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_032():
    source = 'void main() { auto x = +1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", PrefixOp("+", IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_033():
    source = 'void main() { ++x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PrefixOp("++", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_034():
    source = 'void main() { --x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PrefixOp("--", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_035():
    source = 'void main() { x++; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PostfixOp("++", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_036():
    source = 'void main() { x--; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PostfixOp("--", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 7. Expressions - Assignment & Access & Call
# ============================================================================

def test_037():
    source = 'void main() { x = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_038():
    source = 'void main() { x = y = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(AssignExpr(Identifier("x"), AssignExpr(Identifier("y"), IntLiteral(1))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_039():
    source = 'void main() { x.y; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(MemberAccess(Identifier("x"), "y"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_040():
    source = 'void main() { x.y.z; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(MemberAccess(MemberAccess(Identifier("x"), "y"), "z"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_041():
    source = 'void main() { x.y = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(AssignExpr(MemberAccess(Identifier("x"), "y"), IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_042():
    source = 'void main() { foo(); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("foo", []))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_043():
    source = 'void main() { foo(1, 2); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("foo", [IntLiteral(1), IntLiteral(2)]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 8. Statements - If
# ============================================================================

def test_044():
    source = 'void main() { if (1) x = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(IntLiteral(1), ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_045():
    source = 'void main() { if (1) x = 1; else x = 2; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(
                IntLiteral(1),
                ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1))),
                ExprStmt(AssignExpr(Identifier("x"), IntLiteral(2)))
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_046():
    source = 'void main() { if (1) { x = 1; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(
                IntLiteral(1),
                BlockStmt([ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1)))])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 9. Statements - While & For
# ============================================================================

def test_047():
    source = 'void main() { while (1) x = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            WhileStmt(IntLiteral(1), ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_048():
    source = 'void main() { for (;;) x = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ForStmt(None, None, None, ExprStmt(AssignExpr(Identifier("x"), IntLiteral(1))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_049():
    source = 'void main() { for (auto i = 0; i < 10; i++) {} }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ForStmt(
                VarDecl(None, "i", IntLiteral(0)),
                BinaryOp(Identifier("i"), "<", IntLiteral(10)),
                PostfixOp("++", Identifier("i")),
                BlockStmt([])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 10. Statements - Switch
# ============================================================================

def test_050():
    source = 'void main() { switch(x) { case 1: break; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            SwitchStmt(
                Identifier("x"),
                [CaseStmt(IntLiteral(1), [BreakStmt()])]
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_051():
    source = 'void main() { switch(x) { case 1: break; default: break; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            SwitchStmt(
                Identifier("x"),
                [CaseStmt(IntLiteral(1), [BreakStmt()])],
                DefaultStmt([BreakStmt()])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 11. Statements - Jumping
# ============================================================================

def test_052():
    source = 'void main() { return; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ReturnStmt(None)
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_053():
    source = 'void main() { return 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ReturnStmt(IntLiteral(1))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_054():
    source = 'void main() { break; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            BreakStmt()
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_055():
    source = 'void main() { continue; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ContinueStmt()
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 12. Complex & Edge Cases
# ============================================================================

def test_056():
    source = 'void main() { Point p = {1, 2}; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(StructType("Point"), "p", StructLiteral([IntLiteral(1), IntLiteral(2)]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_057():
    source = 'void main() { foo({1, 2}); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("foo", [StructLiteral([IntLiteral(1), IntLiteral(2)])]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_058():
    source = 'void main() { auto x = a.b; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", MemberAccess(Identifier("a"), "b"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_059():
    source = 'void main() { { { } } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            BlockStmt([BlockStmt([])])
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_060():
    source = 'struct S { int a; float b; string c; Point d; };'
    expected = Program([
        StructDecl("S", [
            MemberDecl(IntType(), "a"),
            MemberDecl(FloatType(), "b"),
            MemberDecl(StringType(), "c"),
            MemberDecl(StructType("Point"), "d")
        ])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

# ============================================================================
# 13. Expressions - Detailed
# ============================================================================

def test_061():
    source = 'void main() { auto x = a + b - c; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(BinaryOp(Identifier("a"), "+", Identifier("b")), "-", Identifier("c")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_062():
    source = 'void main() { auto x = a * b / c; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(BinaryOp(Identifier("a"), "*", Identifier("b")), "/", Identifier("c")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_063():
    source = 'void main() { auto x = a + b * c; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(Identifier("a"), "+", BinaryOp(Identifier("b"), "*", Identifier("c"))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_064():
    source = 'void main() { auto x = (a + b) * c; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(BinaryOp(Identifier("a"), "+", Identifier("b")), "*", Identifier("c")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_065():
    source = 'void main() { auto x = !a && b; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(PrefixOp("!", Identifier("a")), "&&", Identifier("b")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_066():
    source = 'void main() { auto x = !(a && b); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", PrefixOp("!", BinaryOp(Identifier("a"), "&&", Identifier("b"))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_067():
    source = 'void main() { auto x = -a * b; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", BinaryOp(PrefixOp("-", Identifier("a")), "*", Identifier("b")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_068():
    source = 'void main() { auto x = a.b.c; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", MemberAccess(MemberAccess(Identifier("a"), "b"), "c"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_069():
    source = 'void main() { a.b = 1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(AssignExpr(MemberAccess(Identifier("a"), "b"), IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_070():
    source = 'void main() { if (a > b) return; else return; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(
                BinaryOp(Identifier("a"), ">", Identifier("b")),
                ReturnStmt(None),
                ReturnStmt(None)
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_071():
    source = 'void main() { while (a < 10) a++; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            WhileStmt(
                BinaryOp(Identifier("a"), "<", IntLiteral(10)),
                ExprStmt(PostfixOp("++", Identifier("a")))
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_072():
    source = 'void main() { for (int i = 0; i < 10; i++) {} }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ForStmt(
                VarDecl(IntType(), "i", IntLiteral(0)),
                BinaryOp(Identifier("i"), "<", IntLiteral(10)),
                PostfixOp("++", Identifier("i")),
                BlockStmt([])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_073():
    source = 'void main() { switch (x) { case 1: case 2: break; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            SwitchStmt(
                Identifier("x"),
                [
                    CaseStmt(IntLiteral(1), []),
                    CaseStmt(IntLiteral(2), [BreakStmt()])
                ]
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_074():
    source = 'void main() { { int x; } { int y; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            BlockStmt([VarDecl(IntType(), "x")]),
            BlockStmt([VarDecl(IntType(), "y")])
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_075():
    source = 'struct Element { int atomicNumber; float mass; string symbol; };'
    expected = Program([
        StructDecl("Element", [
            MemberDecl(IntType(), "atomicNumber"),
            MemberDecl(FloatType(), "mass"),
            MemberDecl(StringType(), "symbol")
        ])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_076():
    source = 'void main() { if (a) if (b) c; else d; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(
                Identifier("a"),
                IfStmt(
                    Identifier("b"),
                    ExprStmt(Identifier("c")),
                    ExprStmt(Identifier("d"))
                )
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_077():
    source = 'void main() { a = b = c = 0; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(AssignExpr(
                Identifier("a"),
                AssignExpr(
                    Identifier("b"),
                    AssignExpr(Identifier("c"), IntLiteral(0))
                )
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_078():
    source = 'void main() { return a + b; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ReturnStmt(BinaryOp(Identifier("a"), "+", Identifier("b")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_079():
    source = 'void main() { f(a, b+c); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("f", [
                Identifier("a"),
                BinaryOp(Identifier("b"), "+", Identifier("c"))
            ]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_080():
    source = 'void main() { auto x = 1.23e-4; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", FloatLiteral(0.000123))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_081():
    source = 'void main() { string s = ""; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(StringType(), "s", StringLiteral(""))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_082():
    source = 'struct Empty {};'
    expected = Program([
        StructDecl("Empty", [])
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_083():
    # Edge cases khó:
    # 1. Unary minus áp lên kết quả function call: -foo()
    #    Dễ nhầm: liệu PrefixOp wraps FuncCall hay parse lỗi?
    # 2. Postfix ++ trên member access: a.b++
    #    Dễ nhầm thứ tự wrap: PostfixOp(MemberAccess) hay MemberAccess(PostfixOp)?
    # 3. Unary ! lên kết quả so sánh: !(a == b)
    #    Dễ nhầm precedence: PrefixOp wraps cả BinaryOp
    source = 'void main() { auto x = -foo(); auto y = a.b++; auto z = !(a == b); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(None, "x", PrefixOp("-", FuncCall("foo", []))),
            VarDecl(None, "y", PostfixOp("++", MemberAccess(Identifier("a"), "b"))),
            VarDecl(None, "z", PrefixOp("!", BinaryOp(Identifier("a"), "==", Identifier("b"))))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_084():
    source = 'void main() { if (x) {} }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(Identifier("x"), BlockStmt([]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_085():
    source = 'void main() { while (true) break; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            WhileStmt(Identifier("true"), BreakStmt())
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_086():
    source = 'void main() { doSomething(); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("doSomething", []))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_087():
    source = 'void main() { x + y; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(Identifier("x"), "+", Identifier("y")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_088():
    source = 'void main() { !x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PrefixOp("!", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_089():
    source = 'void main() { -x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PrefixOp("-", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_090():
    source = 'void main() { +x; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(PrefixOp("+", Identifier("x")))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_091():
    source = 'void main() { a * b + c * d; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(
                BinaryOp(Identifier("a"), "*", Identifier("b")),
                "+",
                BinaryOp(Identifier("c"), "*", Identifier("d"))
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_092():
    source = 'void main() { (a + b) * (c - d); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(
                BinaryOp(Identifier("a"), "+", Identifier("b")),
                "*",
                BinaryOp(Identifier("c"), "-", Identifier("d"))
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_093():
    source = 'void main() { a < b && c > d; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(
                BinaryOp(Identifier("a"), "<", Identifier("b")),
                "&&",
                BinaryOp(Identifier("c"), ">", Identifier("d"))
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_094():
    source = 'void main() { a == b || c != d; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(
                BinaryOp(Identifier("a"), "==", Identifier("b")),
                "||",
                BinaryOp(Identifier("c"), "!=", Identifier("d"))
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_095():
    source = 'void main() { a.x + b.y; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(BinaryOp(
                MemberAccess(Identifier("a"), "x"),
                "+",
                MemberAccess(Identifier("b"), "y")
            ))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_096():
    source = 'void main() { f(g(x)); }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(FuncCall("f", [FuncCall("g", [Identifier("x")])]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_097():
    source = 'void main() { if (x) { y = 1; } else { y = 2; } }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            IfStmt(
                Identifier("x"),
                BlockStmt([ExprStmt(AssignExpr(Identifier("y"), IntLiteral(1)))]),
                BlockStmt([ExprStmt(AssignExpr(Identifier("y"), IntLiteral(2)))])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_098():
    source = 'void main() { for (i=0; i<n; i++) sum = sum + i; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ForStmt(
                ExprStmt(AssignExpr(Identifier("i"), IntLiteral(0))),
                BinaryOp(Identifier("i"), "<", Identifier("n")),
                PostfixOp("++", Identifier("i")),
                ExprStmt(AssignExpr(Identifier("sum"), BinaryOp(Identifier("sum"), "+", Identifier("i"))))
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_099():
    source = 'void main() { int x = -1; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(IntType(), "x", PrefixOp("-", IntLiteral(1)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_100():
    source = 'void main() { float x = +3.14; }'
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            VarDecl(FloatType(), "x", PrefixOp("+", FloatLiteral(3.14)))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_101():
    source = """
    void main() {
        printString("Hello, World!");
    }
    """
    expected = Program([
        FuncDecl(
            VoidType(),
            "main",
            [],
            BlockStmt([
                ExprStmt(
                    FuncCall("printString", [StringLiteral("Hello, World!")])
                )
            ])
        )
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_102():
    source = """
    int add(int x, int y) {
        return x + y;
    }
    
    int multiply(int x, int y) {
        return x * y;
    }
    
    void main() {
        auto a = readInt();
        auto b = readInt();
    
        auto sum = add(a, b);
        auto product = multiply(a, b);
    
        printInt(sum);
        printInt(product);
    }
    """
    expected = Program([
        FuncDecl(
            IntType(),
            "add",
            [Param(IntType(), "x"), Param(IntType(), "y")],
            BlockStmt([
                ReturnStmt(
                    BinaryOp(Identifier("x"), "+", Identifier("y"))
                )
            ])
        ),
        FuncDecl(
            IntType(),
            "multiply",
            [Param(IntType(), "x"), Param(IntType(), "y")],
            BlockStmt([
                ReturnStmt(
                    BinaryOp(Identifier("x"), "*", Identifier("y"))
                )
            ])
        ),
        FuncDecl(
            VoidType(),
            "main",
            [],
            BlockStmt([
                VarDecl(None, "a", FuncCall("readInt", [])),
                VarDecl(None, "b", FuncCall("readInt", [])),
                VarDecl(None, "sum", FuncCall("add", [Identifier("a"), Identifier("b")])),
                VarDecl(None, "product", FuncCall("multiply", [Identifier("a"), Identifier("b")])),
                ExprStmt(FuncCall("printInt", [Identifier("sum")])),
                ExprStmt(FuncCall("printInt", [Identifier("product")]))
            ])
        )
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_103():
    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }
    
    void main() {
        auto num = readInt();
        auto result = factorial(num);
        printInt(result);
    }
    """
    expected = Program([
        FuncDecl(
            IntType(),
            "factorial",
            [Param(IntType(), "n")],
            BlockStmt([
                IfStmt(
                    BinaryOp(Identifier("n"), "<=", IntLiteral(1)),
                    BlockStmt([
                        ReturnStmt(IntLiteral(1))
                    ]),
                    BlockStmt([
                        ReturnStmt(
                            BinaryOp(
                                Identifier("n"),
                                "*",
                                FuncCall(
                                    "factorial",
                                    [BinaryOp(Identifier("n"), "-", IntLiteral(1))]
                                )
                            )
                        )
                    ])
                )
            ])
        ),
        FuncDecl(
            VoidType(),
            "main",
            [],
            BlockStmt([
                VarDecl(None, "num", FuncCall("readInt", [])),
                VarDecl(None, "result", FuncCall("factorial", [Identifier("num")])),
                ExprStmt(FuncCall("printInt", [Identifier("result")]))
            ])
        )
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_104():
    source = """
    struct A {};
    struct B {int a; ID b;};
    struct C {float a; string b;};
    struct D {Z a;};
    """
    expected = Program([
        StructDecl('A', []),
        StructDecl('B', [MemberDecl(IntType(), 'a'), MemberDecl(StructType('ID'), 'b')]),
        StructDecl('C', [MemberDecl(FloatType(), 'a'), MemberDecl(StringType(), 'b')]),
        StructDecl('D', [MemberDecl(StructType('Z'), 'a')]),
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_105():
    source = """
    void main() {
        1;
        1.3;
        "s";
        {};
        {1, {2}};
    }
    """
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(IntLiteral(1)),
            ExprStmt(FloatLiteral(1.3)),
            ExprStmt(StringLiteral("s")),
            ExprStmt(StructLiteral([])),
            ExprStmt(StructLiteral([
                IntLiteral(1),
                StructLiteral([
                    IntLiteral(2)
                ])
            ]))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_106():
    source = """
    void main() {
        for (;;) continue;
        for (a.b=1;a.b;) {}
        for (auto a = 1; ; ) {return;}
    }
    """
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ForStmt(
                None,
                None,
                None,
                ContinueStmt()
            ),
            ForStmt(
                ExprStmt(AssignExpr(
                    MemberAccess(Identifier("a"), "b"),
                    IntLiteral(1)
                )),
                MemberAccess(Identifier("a"), "b"),
                None,
                BlockStmt([])
            ),
            ForStmt(
                VarDecl(None, "a", IntLiteral(1)),
                None,
                None,
                BlockStmt([
                    ReturnStmt(None)
                ])
            )
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)

def test_107():
    source = """
    void main() {
        getPoint().x;
    }
    """
    expected = Program([
        FuncDecl(VoidType(), "main", [], BlockStmt([
            ExprStmt(MemberAccess(FuncCall("getPoint", []), "x"))
        ]))
    ])
    assert str(ASTGenerator(source).generate()) == str(expected)