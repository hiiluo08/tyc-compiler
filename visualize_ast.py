#!/usr/bin/env python
"""
AST Visualizer for TyC compiler test cases.

Usage: 
    # Truyền tên test trực tiếp:
        python visualize_ast.py test_001
        python visualize_ast.py test_083
    # Hoặc gõ số tắt:
        python visualize_ast.py 049
    # Không truyền gì → hiện danh sách rồi nhập:
        python visualize_ast.py

Output: Kết quả trong folder ast_output.
"""

import sys
import os
import re
import inspect
import textwrap
from typing import Optional, List

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphviz import Digraph
from tests.utils import ASTGenerator
from src.utils.nodes import (
    ASTNode, Program, FuncDecl, StructDecl, MemberDecl, Param,
    IntType, FloatType, StringType, VoidType, StructType,
    BlockStmt, VarDecl, IfStmt, WhileStmt, ForStmt,
    SwitchStmt, CaseStmt, DefaultStmt, BreakStmt, ContinueStmt,
    ReturnStmt, ExprStmt,
    BinaryOp, PrefixOp, PostfixOp, AssignExpr, MemberAccess,
    FuncCall, Identifier, StructLiteral,
    IntLiteral, FloatLiteral, StringLiteral,
)

# ---------------------------------------------------------------------------
# Color scheme — grouped by node category
# ---------------------------------------------------------------------------
NODE_COLORS = {
    # Root
    "Program":      "#4A90D9",   # blue
    # Declarations
    "FuncDecl":     "#5BA85B",   # green
    "StructDecl":   "#5BA85B",
    "MemberDecl":   "#A8D5A8",
    "Param":        "#A8D5A8",
    # Types
    "IntType":      "#E8C547",   # amber
    "FloatType":    "#E8C547",
    "StringType":   "#E8C547",
    "VoidType":     "#E8C547",
    "StructType":   "#E8C547",
    # Statements
    "BlockStmt":    "#B0C4DE",   # steel blue
    "VarDecl":      "#87CEEB",
    "IfStmt":       "#C8A0D0",   # purple
    "WhileStmt":    "#C8A0D0",
    "ForStmt":      "#C8A0D0",
    "SwitchStmt":   "#C8A0D0",
    "CaseStmt":     "#D8B8E8",
    "DefaultStmt":  "#D8B8E8",
    "ReturnStmt":   "#F4A0A0",   # salmon
    "BreakStmt":    "#F4A0A0",
    "ContinueStmt": "#F4A0A0",
    "ExprStmt":     "#D3D3D3",   # light gray
    # Expressions
    "BinaryOp":     "#FFD700",   # gold
    "PrefixOp":     "#FFA500",   # orange
    "PostfixOp":    "#FFA500",
    "AssignExpr":   "#FF8C69",   # salmon-orange
    "MemberAccess": "#90EE90",   # light green
    "FuncCall":     "#5CB85C",   # green
    # Identifiers & Literals
    "Identifier":   "#F5F5F5",   # white-ish
    "IntLiteral":   "#FFFACD",   # lemon
    "FloatLiteral": "#FFFACD",
    "StringLiteral":"#FFFACD",
    "StructLiteral":"#FFFFF0",
}
DEFAULT_COLOR = "#FFFFFF"


# ---------------------------------------------------------------------------
# Node → label string
# ---------------------------------------------------------------------------

def node_label(node) -> str:
    cls = type(node).__name__
    if isinstance(node, StructType):
        return f"StructType\n{node.struct_name}"
    if isinstance(node, Identifier):
        return f"Identifier\n{node.name}"
    if isinstance(node, IntLiteral):
        return f"IntLiteral\n{node.value}"
    if isinstance(node, FloatLiteral):
        return f"FloatLiteral\n{node.value}"
    if isinstance(node, StringLiteral):
        val = repr(node.value)
        if len(val) > 20:
            val = val[:17] + '..."'
        return f"StringLiteral\n{val}"
    if isinstance(node, BinaryOp):
        return f"BinaryOp\n[ {node.operator} ]"
    if isinstance(node, PrefixOp):
        return f"PrefixOp\n[ {node.operator} ]"
    if isinstance(node, PostfixOp):
        return f"PostfixOp\n[ {node.operator} ]"
    if isinstance(node, AssignExpr):
        return "AssignExpr\n[ = ]"
    if isinstance(node, MemberAccess):
        return f"MemberAccess\n.{node.member}"
    if isinstance(node, FuncCall):
        return f"FuncCall\n{node.name}"
    if isinstance(node, FuncDecl):
        ret = str(node.return_type) if node.return_type else "auto"
        return f"FuncDecl\n{node.name}\n({ret})"
    if isinstance(node, StructDecl):
        return f"StructDecl\n{node.name}"
    if isinstance(node, MemberDecl):
        return f"MemberDecl\n{node.name}"
    if isinstance(node, Param):
        return f"Param\n{node.name}"
    if isinstance(node, VarDecl):
        t = "auto" if node.var_type is None else str(node.var_type)
        return f"VarDecl\n{node.name}\n({t})"
    if isinstance(node, StructLiteral):
        return "StructLiteral\n{ … }"
    return cls


# ---------------------------------------------------------------------------
# Collect children of a node
# ---------------------------------------------------------------------------

def node_children(node) -> list:
    if isinstance(node, Program):
        return node.decls
    if isinstance(node, FuncDecl):
        ch = []
        if node.return_type:
            ch.append(node.return_type)
        ch.extend(node.params)
        ch.append(node.body)
        return ch
    if isinstance(node, StructDecl):
        return node.members
    if isinstance(node, MemberDecl):
        return [node.member_type]
    if isinstance(node, Param):
        return [node.param_type]
    if isinstance(node, BlockStmt):
        return node.statements
    if isinstance(node, VarDecl):
        ch = []
        if node.var_type:
            ch.append(node.var_type)
        if node.init_value:
            ch.append(node.init_value)
        return ch
    if isinstance(node, IfStmt):
        ch = [node.condition, node.then_stmt]
        if node.else_stmt:
            ch.append(node.else_stmt)
        return ch
    if isinstance(node, WhileStmt):
        return [node.condition, node.body]
    if isinstance(node, ForStmt):
        ch = []
        if node.init:
            ch.append(node.init)
        if node.condition:
            ch.append(node.condition)
        if node.update:
            ch.append(node.update)
        ch.append(node.body)
        return ch
    if isinstance(node, SwitchStmt):
        ch = [node.expr] + node.cases
        if node.default_case:
            ch.append(node.default_case)
        return ch
    if isinstance(node, CaseStmt):
        return [node.expr] + node.statements
    if isinstance(node, DefaultStmt):
        return node.statements
    if isinstance(node, ReturnStmt):
        return [node.expr] if node.expr else []
    if isinstance(node, ExprStmt):
        return [node.expr]
    if isinstance(node, BinaryOp):
        return [node.left, node.right]
    if isinstance(node, (PrefixOp, PostfixOp)):
        return [node.operand]
    if isinstance(node, AssignExpr):
        return [node.lhs, node.rhs]
    if isinstance(node, MemberAccess):
        return [node.obj]
    if isinstance(node, FuncCall):
        return node.args
    if isinstance(node, StructLiteral):
        return node.values
    return []


# ---------------------------------------------------------------------------
# Recursively add nodes to a Graphviz subgraph
# ---------------------------------------------------------------------------

_counter = [0]

def _new_id(prefix: str) -> str:
    _counter[0] += 1
    return f"{prefix}_{_counter[0]}"


def add_tree(graph, node, parent_id: Optional[str], prefix: str):
    if node is None:
        return
    nid = _new_id(prefix)

    # --- Lấy label và màu, bắt lỗi attribute ---
    try:
        cls = type(node).__name__
        lbl = node_label(node)
        clr = NODE_COLORS.get(cls, DEFAULT_COLOR)
    except AttributeError as e:
        cls = type(node).__name__
        lbl = f"⚠ {cls}\nAttributeError:\n{e}"
        clr = "#FF4444"

    graph.node(
        nid,
        label=lbl,
        style="filled",
        fillcolor=clr,
        shape="box",
        fontname="Helvetica",
        fontsize="11",
        margin="0.12,0.06",
    )
    if parent_id is not None:
        graph.edge(parent_id, nid, arrowsize="0.7")

    # --- Lấy children, bắt lỗi attribute khi traverse ---
    try:
        children = node_children(node)
    except AttributeError as e:
        err_id = _new_id(prefix)
        graph.node(
            err_id,
            label=f"⚠ AttributeError\n(children):\n{e}",
            style="filled",
            fillcolor="#FF4444",
            shape="note",
            fontname="Helvetica",
            fontsize="10",
        )
        graph.edge(nid, err_id, arrowsize="0.7", color="red")
        return

    for child in children:
        add_tree(graph, child, nid, prefix)


# ---------------------------------------------------------------------------
# Extract source and expected from a test function
# ---------------------------------------------------------------------------

def extract_test_data(test_module, test_name: str):
    func = getattr(test_module, test_name, None)
    if func is None:
        return None, None

    raw = inspect.getsource(func)
    raw = textwrap.dedent(raw)

    # Strip the 'def testXXX():' line(s) at the top
    lines = raw.splitlines()
    body_lines = []
    skip = True
    for line in lines:
        if skip and re.match(r'^def\s', line):
            skip = False
            continue
        if not skip:
            body_lines.append(line)
    body = textwrap.dedent("\n".join(body_lines))

    body = re.sub(r"^\s*assert\s+.*$", "pass", body, flags=re.MULTILINE)

    body = re.sub(r"^\s*pass\s*$", "pass", body, flags=re.MULTILINE)

    ns = {
        "Program": Program, "FuncDecl": FuncDecl, "StructDecl": StructDecl,
        "MemberDecl": MemberDecl, "Param": Param,
        "IntType": IntType, "FloatType": FloatType, "StringType": StringType,
        "VoidType": VoidType, "StructType": StructType,
        "BlockStmt": BlockStmt, "VarDecl": VarDecl, "IfStmt": IfStmt,
        "WhileStmt": WhileStmt, "ForStmt": ForStmt,
        "SwitchStmt": SwitchStmt, "CaseStmt": CaseStmt,
        "DefaultStmt": DefaultStmt, "BreakStmt": BreakStmt,
        "ContinueStmt": ContinueStmt, "ReturnStmt": ReturnStmt,
        "ExprStmt": ExprStmt,
        "BinaryOp": BinaryOp, "PrefixOp": PrefixOp, "PostfixOp": PostfixOp,
        "AssignExpr": AssignExpr, "MemberAccess": MemberAccess,
        "FuncCall": FuncCall, "Identifier": Identifier,
        "StructLiteral": StructLiteral,
        "IntLiteral": IntLiteral, "FloatLiteral": FloatLiteral,
        "StringLiteral": StringLiteral,
        "None": None, "True": True, "False": False,
    }
    try:
        exec(body, ns)
    except Exception as e:
        print(f"  [!] Error executing test body: {e}")
        return None, None

    return ns.get("source"), ns.get("expected")


# ---------------------------------------------------------------------------
# Build and render the side-by-side graph
# ---------------------------------------------------------------------------

def visualize(test_name: str, output_dir: str = "ast_output"):
    os.makedirs(output_dir, exist_ok=True)

    import tests.test_ast_gen as test_module

    _counter[0] = 0

    print(f"\n→ Extracting test data for '{test_name}'...")
    source, expected = extract_test_data(test_module, test_name)

    if source is None:
        print(f"  [!] Test '{test_name}' not found or has no source/expected.")
        return

    try:
        actual = ASTGenerator(source).generate()
    except Exception as e:
        print(f"  [!] ASTGenerator error: {e}")
        actual = None

    dot = Digraph(
        name=test_name,
        comment=f"AST visualization — {test_name}",
        graph_attr={
            "rankdir": "TB",
            "splines": "ortho",
            "nodesep": "0.4",
            "ranksep": "0.5",
            "fontname": "Helvetica",
            "fontsize": "12",
            "label": f"AST Comparison — {test_name}",
            "labelloc": "t",
            "labeljust": "c",
        },
    )

    # Expected
    with dot.subgraph(name="cluster_expected") as c:
        c.attr(
            label="Expected AST",
            style="filled",
            fillcolor="#F0F8FF",
            color="#4A90D9",
            penwidth="2",
            fontname="Helvetica-Bold",
            fontsize="13",
        )
        if expected is not None:
            add_tree(c, expected, None, "e")
        else:
            c.node("e_none", "No expected\ndefined", shape="note", fillcolor="#FFE4E1", style="filled")

    #Actual
    with dot.subgraph(name="cluster_actual") as c:
        c.attr(
            label="Actual Output",
            style="filled",
            fillcolor="#F0FFF0",
            color="#5BA85B",
            penwidth="2",
            fontname="Helvetica-Bold",
            fontsize="13",
        )
        if actual is not None:
            add_tree(c, actual, None, "a")
        else:
            c.node("a_none", "Generation\nfailed", shape="note", fillcolor="#FFE4E1", style="filled")

    # Match check
    if actual is not None and expected is not None:
        match = str(actual) == str(expected)
        status = "✓  MATCH" if match else "✗  MISMATCH"
        color  = "green" if match else "red"
        print(f"  Result: {status}")
    else:
        color  = "gray"
        status = "N/A"

    # Footer node showing match status
    dot.node(
        "status",
        label=f"Result: {status}",
        shape="rectangle",
        style="filled",
        fillcolor="#EAFFEA" if status.startswith("✓") else "#FFEAEA",
        fontname="Helvetica-Bold",
        fontsize="13",
        color=color,
        penwidth="2",
    )

    # Render
    out_path = os.path.join(output_dir, test_name)
    dot.render(out_path, format="pdf", view=True, cleanup=True)
    print(f"  Saved → {out_path}.pdf  (also opened automatically)")


# ---------------------------------------------------------------------------
# Main — interactive or CLI
# ---------------------------------------------------------------------------

def list_tests(test_module) -> List[str]:
    return sorted(
        name for name in dir(test_module)
        if name.startswith("test_") and callable(getattr(test_module, name))
    )


def main():
    import tests.test_ast_gen as test_module

    if len(sys.argv) > 1:
        test_name = sys.argv[1].strip()
    else:
        tests = list_tests(test_module)
        print("Available tests:")
        for i, t in enumerate(tests):
            end = "\n" if (i + 1) % 5 == 0 else "  "
            print(f"  {t}", end=end)
        print()
        test_name = input("\nEnter test name: ").strip()

    if not test_name:
        print("No test name provided.")
        sys.exit(1)

    if not test_name.startswith("test_"):
        test_name = "test_" + test_name

    visualize(test_name)


if __name__ == "__main__":
    main()
