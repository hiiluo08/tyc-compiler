# """
# Parser test cases for TyC compiler
# Comprehensive test suite covering all syntactic structures
# """
# import pytest
# from tests.utils import Parser

# # ============================================================================
# # 1. PROGRAM STRUCTURE & DECLARATIONS
# # ============================================================================

# def test_001_minimal_program():
#     """Minimal valid program with just main"""
#     source = "void main() {}"
#     assert Parser(source).parse() == "success"

# def test_002_program_with_empty_main():
#     source = "void main() { ; }"
#     assert Parser(source).parse() == "Error on line 1 col 14: ;"

# def test_003_multiple_functions():
#     source = """
#     void func1() {}
#     int func2() { return 1; }
#     void main() {}
#     """
#     assert Parser(source).parse() == "success"

# def test_004_struct_declarations():
#     source = """
#     struct Point { int x; int y; };
#     struct Rect { Point p1; Point p2; };
#     void main() {}
#     """
#     assert Parser(source).parse() == "success"

# def test_005_mixed_order():
#     """Structs must generally appear before use in C-like, but parser just sees decls.
#     Grammar usually allows any order or sequence."""
#     source = """
#     struct A { int a; };
#     void foo() {}
#     struct B { float b; };
#     void main() {}
#     """
#     assert Parser(source).parse() == "success"

# def test_006_empty_file():
#     """Empty file might be allowed or not depending on grammar start rule"""
#     source = ""
#     # Usually expect at least one declaration or EOF
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 2. FUNCTION DECLARATIONS
# # ============================================================================

# def test_007_func_no_params_void():
#     assert Parser("void f() {}").parse() == "success"

# def test_008_func_explicit_return():
#     assert Parser("int f() { return 1; }").parse() == "success"

# def test_009_func_inferred_return():
#     assert Parser("f() { return 1; }").parse() == "success"

# def test_010_func_one_param():
#     assert Parser("void f(int a) {}").parse() == "success"

# def test_011_func_multiple_params():
#     assert Parser("void f(int a, float b, string c) {}").parse() == "success"

# def test_012_func_struct_param():
#     assert Parser("void f(Point p) {}").parse() == "success"

# def test_013_func_missing_body():
#     source = "void f();"
#     assert Parser(source).parse() == "Error on line 1 col 8: ;"

# def test_014_func_auto_param_error():
#     source = "void f(auto x) {}"
#     assert Parser(source).parse() == "Error on line 1 col 7: auto"

# def test_015_func_missing_param_name():
#     source = "void f(int) {}"
#     assert Parser(source).parse() == "Error on line 1 col 10: )"

# def test_016_func_missing_param_type():
#     source = "void f(x) {}"
#     assert Parser(source).parse() == "Error on line 1 col 8: )"

# def test_017_func_comma_error():
#     source = "void f(int a,) {}"
#     assert Parser(source).parse() == "Error on line 1 col 13: )"

# # ============================================================================
# # 3. STRUCT DECLARATIONS
# # ============================================================================

# def test_018_struct_basic():
#     source = "struct A { int x; };"
#     assert Parser(source).parse() == "success"

# def test_019_struct_multiple_members():
#     source = "struct A { int x; float y; string z; };"
#     assert Parser(source).parse() == "success"

# def test_020_struct_empty():
#     source = "struct A {};"
#     assert Parser(source).parse() == "success"

# def test_021_struct_missing_semicolon_member():
#     source = "struct A { int x }"
#     assert Parser(source).parse() == "Error on line 1 col 17: }"

# def test_022_struct_missing_semicolon_end():
#     source = "struct A { int x; } void main() {}"
#     # Parser might consume struct and fail on 'void' if ';' is missing
#     # or expect EOF. TyC struct requires ';' after '}'
#     assert Parser(source).parse() == "Error on line 1 col 20: void"

# def test_023_struct_nested_error():
#     source = "struct A { struct B { int x; }; };"
#     assert Parser(source).parse() == "Error on line 1 col 11: struct"

# def test_024_struct_auto_member_error():
#     source = "struct A { auto x; };"
#     assert Parser(source).parse() == "Error on line 1 col 11: auto"

# def test_025_struct_init_expr_as_member_error():
#     source = "struct A { int x = 5; };"
#     assert Parser(source).parse() == "Error on line 1 col 17: ="

# # ============================================================================
# # 4. VARIABLE DECLARATIONS
# # ============================================================================

# def test_026_var_decl_explicit_no_init():
#     source = "void main() { int x; }"
#     assert Parser(source).parse() == "success"

# def test_027_var_decl_explicit_init():
#     source = "void main() { int x = 10; }"
#     assert Parser(source).parse() == "success"

# def test_028_var_decl_auto_init():
#     source = "void main() { auto x = 10; }"
#     assert Parser(source).parse() == "success"

# def test_029_var_decl_auto_no_init():
#     source = "void main() { auto x; }"
#     assert Parser(source).parse() == "success"

# def test_030_var_decl_struct_type():
#     source = "void main() { Point p; }"
#     assert Parser(source).parse() == "success"

# def test_031_var_decl_multiple_same_line_error():
#     # Spec doesn't explicitly forbid `int x, y;` but examples show one per line.
#     # Standard C allows it. Spec: "<type> <identifier>"
#     # If grammar is "type ID (ASSIGN expr)? SEMI", then "int x, y;" is invalid.
#     # Let's assume strict grammar from spec: "<type> <identifier>"
#     source = "void main() { int x, y; }"
#     # Based on existing test_024, this is an Error.
#     assert Parser(source).parse() == "Error on line 1 col 19: ,"

# # ============================================================================
# # 5. BLOCK STATEMENTS
# # ============================================================================

# def test_032_empty_block():
#     source = "void main() { {} }"
#     assert Parser(source).parse() == "success"

# def test_033_nested_blocks():
#     source = "void main() { { { int x; } } }"
#     assert Parser(source).parse() == "success"

# def test_034_block_mixed_stmts():
#     source = "void main() { int x; x = 1; { int y; y = x; } }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 6. IF STATEMENTS
# # ============================================================================

# def test_035_if_simple():
#     source = "void main() { if (1) return; }"
#     assert Parser(source).parse() == "success"

# def test_036_if_else():
#     source = "void main() { if (1) return; else return; }"
#     assert Parser(source).parse() == "success"

# def test_037_if_block():
#     source = "void main() { if (1) { int x; } }"
#     assert Parser(source).parse() == "success"

# def test_038_if_nested():
#     source = "void main() { if (x) if (y) return; else return; }"
#     assert Parser(source).parse() == "success"

# def test_039_if_condition_error():
#     source = "void main() { if 1 return; }" # Missing parens
#     assert Parser(source).parse() == "Error on line 1 col 17: 1"

# def test_040_if_empty_body_error():
#     # "if (expr) stmt". Is empty string a stmt? No. ";" is an expression statement (invalid expr?) 
#     # Or strict Stmt rule? Spec: "A semicolon (;) by itself does not constitute a valid statement"
#     # So `if (x) ;` should be Error?
#     source = "void main() { if (x) ; }"
#     # Based on Spec: "; by itself does not constitute a valid statement".
#     # So this should check if Empty Statement is supported.
#     # Usually parsers allow it, but TyC spec says NO.
#     assert Parser(source).parse() == "Error on line 1 col 21: ;"

# def test_041_dangling_else_associativity():
#     # Should associate with nearest if
#     source = "void main() { if (a) if (b) s1; else s2; }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 7. WHILE STATEMENTS
# # ============================================================================

# def test_042_while_simple():
#     source = "void main() { while(1) { break; } }"
#     assert Parser(source).parse() == "success"

# def test_043_while_single_stmt():
#     source = "void main() { while(x > 0) x--; }"
#     assert Parser(source).parse() == "success"

# def test_044_while_missing_parens():
#     source = "void main() { while x > 0 {} }"
#     assert Parser(source).parse() == "Error on line 1 col 20: x"

# # ============================================================================
# # 8. FOR STATEMENTS
# # ============================================================================

# def test_045_for_full():
#     source = "void main() { for (int i=0; i<10; i++) {} }"
#     assert Parser(source).parse() == "success"

# def test_046_for_no_init():
#     source = "void main() { for (; i<10; i++) {} }"
#     assert Parser(source).parse() == "success"

# def test_047_for_no_cond():
#     source = "void main() { for (int i=0; ; i++) {} }"
#     assert Parser(source).parse() == "success"

# def test_048_for_no_update():
#     source = "void main() { for (int i=0; i<10; ) {} }"
#     assert Parser(source).parse() == "success"

# def test_049_for_empty_header():
#     source = "void main() { for (;;) {} }"
#     assert Parser(source).parse() == "success"

# def test_050_for_auto_init():
#     source = "void main() { for (auto i=0; i<10; ++i) {} }"
#     assert Parser(source).parse() == "success"

# def test_051_for_assignment_init():
#     source = "void main() { for (i=0; i<10; i++) {} }"
#     assert Parser(source).parse() == "success"

# def test_052_for_bad_semicolons():
#     source = "void main() { for (i=0, j=0; i<10) {} }"
#     assert Parser(source).parse() == "Error on line 1 col 22: ,"

# # ============================================================================
# # 9. SWITCH STATEMENTS
# # ============================================================================

# def test_053_switch_basic():
#     source = """
#     void main() {
#         switch (x) {
#             case 1: break;
#             default: break;
#         }
#     }
#     """
#     assert Parser(source).parse() == "success"

# def test_054_switch_no_default():
#     source = "void main() { switch(x) { case 1: break; } }"
#     assert Parser(source).parse() == "success"

# def test_055_switch_empty_body():
#     source = "void main() { switch(x) {} }"
#     assert Parser(source).parse() == "success"

# def test_056_switch_multiple_cases():
#     source = """
#     void main() {
#         switch(x) {
#             case 1:
#             case 2:
#                 x++;
#                 break;
#         }
#     }
#     """
#     assert Parser(source).parse() == "success"

# def test_057_switch_constant_expr():
#     source = "void main() { switch(x) { case 1+2: break; } }"
#     assert Parser(source).parse() == "success"

# def test_058_switch_bad_colon():
#     source = "void main() { switch(x) { case 1; break; } }"
#     assert Parser(source).parse() == "Error on line 1 col 32: ;"

# # ============================================================================
# # 10. JUMP STATEMENTS
# # ============================================================================

# def test_059_break():
#     source = "void main() { while(1) break; }"
#     assert Parser(source).parse() == "success"

# def test_060_continue():
#     source = "void main() { while(1) continue; }"
#     assert Parser(source).parse() == "success"

# def test_061_return_val():
#     source = "void main() { return 1; }"
#     assert Parser(source).parse() == "success"

# def test_062_return_void():
#     source = "void main() { return; }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 11. EXPRESSIONS - ARITHMETIC
# # ============================================================================

# def test_063_expr_add_sub():
#     source = "void main() { x = a + b - c; }"
#     assert Parser(source).parse() == "success"

# def test_064_expr_mul_div_mod():
#     source = "void main() { x = a * b / c % d; }"
#     assert Parser(source).parse() == "success"

# def test_065_expr_precedence_mul_add():
#     # a + b * c -> a + (b * c)
#     source = "void main() { x = a + b * c; }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 12. EXPRESSIONS - RELATIONAL & LOGICAL
# # ============================================================================

# def test_066_expr_relational():
#     source = "void main() { bool = a < b && c >= d; }"
#     assert Parser(source).parse() == "success"

# def test_067_expr_equality():
#     source = "void main() { bool = a == b || c != d; }"
#     assert Parser(source).parse() == "success"

# def test_068_expr_logical_precedence():
#     # && higher than ||
#     source = "void main() { bool = a && b || c && d; }"
#     assert Parser(source).parse() == "success"

# def test_069_expr_not():
#     source = "void main() { bool = !a && !(b || c); }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 13. EXPRESSIONS - UNARY & POSTFIX
# # ============================================================================

# def test_070_expr_unary_minus():
#     source = "void main() { x = -a + -b; }"
#     assert Parser(source).parse() == "success"

# def test_071_expr_increment_prefix():
#     source = "void main() { ++x; --y; }"
#     assert Parser(source).parse() == "success"

# def test_072_expr_increment_postfix():
#     source = "void main() { x++; y--; }"
#     assert Parser(source).parse() == "success"

# def test_073_expr_postfix_precedence():
#     # a.b++ should parse as (a.b)++
#     source = "void main() { a.b++; }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 14. EXPRESSIONS - MEMBER ACCESS & CALLS
# # ============================================================================

# def test_074_member_access():
#     source = "void main() { x = p.x; }"
#     assert Parser(source).parse() == "success"

# def test_075_nested_member_access():
#     source = "void main() { x = rect.p1.x; }"
#     assert Parser(source).parse() == "success"

# def test_076_function_call_no_args():
#     source = "void main() { foo(); }"
#     assert Parser(source).parse() == "success"

# def test_077_function_call_args():
#     source = "void main() { foo(1, a+b, \"s\"); }"
#     assert Parser(source).parse() == "success"

# def test_078_method_like_call_error():
#     # TyC strict: <identifier>(args) for calls.
#     # p.foo() might not be valid if member access must result in struct member?
#     # Spec: "Struct members can be struct types... struct members are accessed using dot".
#     # Spec: Function declaration is top level. Structs have data members.
#     # So `obj.method()` is NOT valid syntax in TyC (no methods).
#     source = "void main() { p.foo(); }"
#     # Parser should flag this if grammar restricts postfix to `ID ( args )`
#     # However, if grammar is `expr ( args )`, then `p.foo` is an expr.
#     # But `p.foo` refers to a member. If member is function pointer? TyC doesn't have func pointers.
#     # So `p.foo()` is semantically invalid, but SYNTACTICALLY?
#     # Usually `expr DOT ID` is an l-value. `expr LPAREN ...` is a call.
#     # If grammar allows `expression '(' arg_list ')'`, and `expression` includes `expr '.' ID`, then it parses.
#     # But TyC spec says: "Function call ... has the form: <identifier>(<argument_list>)".
#     # It strictly says `<identifier>(...)`, NOT `<expression>(...)`.
#     # So `p.foo()` should be a SYNTAX ERROR.
#     assert Parser(source).parse() == "Error on line 1 col 19: ("

# # ============================================================================
# # 15. EXPRESSIONS - ASSIGNMENT
# # ============================================================================

# def test_079_assign_simple():
#     source = "void main() { x = 1; }"
#     assert Parser(source).parse() == "success"

# def test_080_assign_chained():
#     source = "void main() { x = y = z = 0; }"
#     assert Parser(source).parse() == "success"

# def test_081_assign_to_member():
#     source = "void main() { p.x = 10; }"
#     assert Parser(source).parse() == "success"

# def test_082_assign_to_expr_error():
#     source = "void main() { (a+b) = 5; }"
#     # Syntax error: LHS of assignment must be l-value (ID or member access)
#     # Spec says: "<identifier> = <expr>" or "<member_access> = <expr>"
#     assert Parser(source).parse() == "Error on line 1 col 20: ="

# # ============================================================================
# # 16. LITERALS & STRUCT INIT
# # ============================================================================

# def test_083_literals_in_expr():
#     source = "void main() { x = 1 + 2.5 + \"str\"; }" 
#     # Semantically wrong, but syntactically valid expression
#     assert Parser(source).parse() == "success"

# def test_084_struct_init_empty():
#     source = "void main() { Point p = {}; }" # Spec allows empty? "or empty for an empty struct"
#     # Wait, "comma-separated list ... or empty". So {} is valid.
#     assert Parser(source).parse() == "success"

# def test_085_struct_init_values():
#     source = "void main() { Point p = {1, 2}; }"
#     assert Parser(source).parse() == "success"

# def test_086_struct_init_nested():
#     source = "void main() { Rect r = {{0,0}, {1,1}}; }"
#     assert Parser(source).parse() == "success"

# # ============================================================================
# # 17. COMPLEX COMBINATIONS
# # ============================================================================

# def test_087_complex_calc():
#     source = """
#     void main() {
#         auto x = (-b + sqrt(b*b - 4*a*c)) / (2*a);
#     }
#     """
#     assert Parser(source).parse() == "success"

# def test_088_deep_nesting():
#     source = """
#     void main() {
#         while(true) {
#             if (x) {
#                 for(;;) {
#                     switch(y) {
#                         case 1: {
#                             if (z) break;
#                         }
#                     }
#                 }
#             }
#         }
#     }
#     """
#     assert Parser(source).parse() == "success"

# def test_089_array_access_error():
#     # TyC has no arrays
#     source = "void main() { x[0] = 1; }"
#     assert Parser(source).parse() == "Error Token ["

# def test_090_ternary_operator_error():
#     source = "void main() { x = c ? 1 : 0; }"
#     assert Parser(source).parse() == "Error Token ?"

# # ============================================================================
# # 18. MORE EDGE CASES
# # ============================================================================

# def test_091_string_literal_chars():
#     source = 'void main() { s = "Hello \\n World"; }'
#     assert Parser(source).parse() == "success"

# def test_092_float_scientific():
#     source = "void main() { f = 1.23e-4; }"
#     assert Parser(source).parse() == "success"

# def test_093_comments_handling():
#     source = """
#     /* Block comment */
#     void main() {
#         // Line comment
#         int x; // EOL comment
#     }
#     """
#     assert Parser(source).parse() == "success"

# def test_094_return_expr_mismatch_syntax():
#     # Parser accepts any expr in return
#     source = "void main() { return 1+2*3; }"
#     assert Parser(source).parse() == "success"

# def test_095_struct_decl_inside_func_error():
#     # Nesting check
#     source = "void main() { struct A { int x; }; }"
#     assert Parser(source).parse() == "Error on line 1 col 14: struct"

# def test_096_func_decl_inside_func_error():
#     source = "void main() { void foo() {} }"
#     assert Parser(source).parse() == "Error on line 1 col 14: void"

# def test_097_identifier_keywords_error():
#     source = "void if() {}"
#     assert Parser(source).parse() == "Error on line 1 col 5: if"

# def test_098_case_scope():
#     source = "void main() { switch(x) { case 1: int y; y=1; break; } }"
#     assert Parser(source).parse() == "success"

# def test_099_statement_expr():
#     source = "void main() { 1 + 2; }"
#     assert Parser(source).parse() == "success"

# def test_100_empty_statement():
#     source = "void main() { ; }"
#     assert Parser(source).parse() == "Error on line 1 col 14: ;"

# def test_101_block_scope_vars():
#     source = "void main() { { int x; } { int x; } }"
#     assert Parser(source).parse() == "success"

# def test_102_comparison_chain_syntax():
#     source = "void main() { if (a < b < c) {} }"
#     assert Parser(source).parse() == "success"

# def test_103_bad_token():
#     source = "void main() { @ }"
#     assert Parser(source).parse() == "Error Token @"

# def test_104_missing_brace():
#     source = "void main() { "
#     assert Parser(source).parse() == "Error on line 1 col 14: <EOF>"

# def test_105_extra_brace():
#     source = "void main() { } }"
#     assert Parser(source).parse() == "Error on line 1 col 16: }"

# def test_106_missing_paren_if():
#     source = "void main() { if x {} }"
#     assert Parser(source).parse() == "Error on line 1 col 17: x"

# def test_107_function_call_empty_args():
#     source = "void main() { f(); }"
#     assert Parser(source).parse() == "success"

# def test_108_function_call_trailing_comma():
#     source = "void main() { f(1, ); }"
#     assert Parser(source).parse() == "Error on line 1 col 19: )"

# def test_109_struct_init_trailing_comma():
#     source = "void main() { Point p = {1, }; }"
#     assert Parser(source).parse() == "Error on line 1 col 28: }"

# def test_110_program_just_comments():
#     source = "// just comments"
#     assert Parser(source).parse() == "success"

# """
# Parser test cases for TyC compiler
# Each test_* function represents ONE test case.
# Expected output is embedded directly in code.
# Actual output is written to .txt file per test.
# """

# import os
# import pytest
# from tests.utils import Parser

# def run_parser_test(test_name: str, source: str, expected: str, n_match: bool = False):
#     parser = Parser(source)
#     output = parser.parse()

#     assert output == expected, f"Output: {output}. Expected: {expected}"

# def test_1():
#     source = ""
#     expected = "success"
#     run_parser_test("1", source, expected)

# def test_2():
#     source = "void main(){ int a; } "
#     expected = "success"
#     run_parser_test("2", source, expected)

# def test_3():
#     source = "void main(){ float a; string a; auto a; }"
#     expected = "success"
#     run_parser_test("3", source, expected)

# def test_4():
#     source = "void main(){ int a, b, c; }"
#     expected = "Error on line 1 col 18: ,"
#     run_parser_test("4", source, expected)

# def test_5():
#     source = "void main(){ float a = -1e5; }"
#     expected = "success"
#     run_parser_test("5", source, expected)

# def test_6():
#     source = "void main(){ string s = \"Trung4n\"; }"
#     expected = "success"
#     run_parser_test("6", source, expected)

# def test_7():
#     source = "void main(){ auto u = 1; auto i = -100.0; auto a = \"uia\"; }"
#     expected = "success"
#     run_parser_test("7", source, expected)

# def test_8():
#     source = "void main(){ int k = i + j; }"
#     expected = "success"
#     run_parser_test("8", source, expected)

# def test_9():
#     source = "void main(){ float i }"
#     expected = "Error on line 1 col 21: }"
#     run_parser_test("9", source, expected)

# def test_10():
#     source = "void main(){ string i,; }"
#     expected = "Error on line 1 col 21: ,"
#     run_parser_test("10", source, expected)

# def test_11():
#     source = "void main(){ auto i,,a; }"
#     expected = "Error on line 1 col 19: ,"
#     run_parser_test("11", source, expected)

# def test_12():
#     source = "void main(){ int i = 5,5; }"
#     expected = "Error on line 1 col 22: ,"
#     run_parser_test("12", source, expected)

# def test_13():
#     source = "void main(){ int a b; }"
#     expected = "Error on line 1 col 19: b"
#     run_parser_test("13", source, expected)

# def test_14():
#     source = "void main(){ int a = = b; }"
#     expected = "Error on line 1 col 21: ="
#     run_parser_test("14", source, expected)

# def test_15():
#     source = "void main(){ int a = ; }"
#     expected = "Error on line 1 col 21: ;"
#     run_parser_test("15", source, expected)

# def test_16():
#     source = "void main(){ int = 5; }"
#     expected = "Error on line 1 col 17: ="
#     run_parser_test("16", source, expected)

# def test_17():
#     source = "void main(){ float x = int; }"
#     expected = "Error on line 1 col 23: int"
#     run_parser_test("17", source, expected)

# def test_18():
#     source = "void main(){ int; }"
#     expected = "Error on line 1 col 16: ;"
#     run_parser_test("18", source, expected)

# def test_19():
#     source = "void main(){ int int; }"
#     expected = "Error on line 1 col 17: int"
#     run_parser_test("19", source, expected)

# def test_20():
#     source = "void main(){ int a = 5, string b = \"here we go\"; }"
#     expected = "Error on line 1 col 22: ,"
#     run_parser_test("20", source, expected)

# def test_21():
#     source = "void main(){ void a = 5; }"
#     expected = "Error on line 1 col 13: void"
#     run_parser_test("21", source, expected)

# def test_22():
#     source = "void main(){ Point a; }"
#     expected = "success"
#     run_parser_test("22", source, expected)

# def test_23():
#     source = "void main(){ in t; }"
#     expected = "success"
#     run_parser_test("23", source, expected)

# def test_24():
#     source = "void main(){ Cat moew = moew; }"
#     expected = "success"
#     run_parser_test("24", source, expected)

# def test_25():
#     source = "void main(){ Dog husky; }"
#     expected = "success"
#     run_parser_test("25", source, expected)

# def test_26():
#     source = "struct Point{" \
#              "  int a;" \
#              "  int b;" \
#              "};"
#     expected = "success"
#     run_parser_test("26", source, expected)

# def test_27():
#     source = "struct Point{" \
#              "};"
#     expected = "success"
#     run_parser_test("27", source, expected)

# def test_28():
#     source = "struct A{" \
#              "  int a;" \
#              "  float b;" \
#              "  string c;" \
#              "};"
#     expected = "success"
#     run_parser_test("28", source, expected)

# def test_29():
#     source = "struct Node{" \
#              "  int val;" \
#              "  Node next;" \
#              "};"
#     expected = "success"
#     run_parser_test("29", source, expected)

# def test_30():
#     source = "struct B{" \
#              "  auto uia;" \
#              "};"
#     expected = "Error on line 1 col 11: auto"
#     run_parser_test("30", source, expected)

# def test_31():
#     source = "struct C{" \
#              " void via;" \
#              "};"
#     expected = "Error on line 1 col 10: void"
#     run_parser_test("31", source, expected)

# def test_32():
#     source = "struct D{" \
#              " if (a == 5) int b = a;" \
#              "};"
#     expected = "Error on line 1 col 10: if"
#     run_parser_test("32", source, expected)

# def test_33():
#     source = "struct D{" \
#              "  float pi;" \
#              "}"
#     expected = "Error on line 1 col 21: <EOF>"
#     run_parser_test("33", source, expected)

# def test_34():
#     source = "struct D{" \
#              "  float pi" \
#              "}"
#     expected = "Error on line 1 col 19: }"
#     run_parser_test("34", source, expected)

# def test_35():
#     source = "struct D{" \
#              "  float pi = 3.14;" \
#              "};"
#     expected = "Error on line 1 col 20: ="
#     run_parser_test("35", source, expected)

# def test_36():
#     source = "struct Cat{" \
#              "  string name, tail;" \
#              "};"
#     expected = "Error on line 1 col 24: ,"
#     run_parser_test("36", source, expected)

# def test_37():
#     source = "struct Cat" \
#              "  string name, tail;" \
#              "};"
#     expected = "Error on line 1 col 12: string"
#     run_parser_test("37", source, expected)

# def test_38():
#     source = "struct LinkedList{" \
#              "  struct Node{" \
#              "    int val;" \
#              "  };" \
#              "};"
#     expected = "Error on line 1 col 20: struct"
#     run_parser_test("38", source, expected)

# def test_39():
#     source = "Animal{" \
#              "};"
#     expected = "Error on line 1 col 6: {"
#     run_parser_test("39", source, expected)

# def test_40():
#     source = "struct Dog{" \
#              "  string name;;" \
#              "};"
#     expected = "Error on line 1 col 25: ;"
#     run_parser_test("40", source, expected)

# def test_41():
#     source = "struct String{" \
#              "  string;" \
#              "};"
#     expected = "Error on line 1 col 22: ;"
#     run_parser_test("41", source, expected)

# def test_42():
#     source = "struct{" \
#              "  string s;" \
#              "};"
#     expected = "Error on line 1 col 6: {"
#     run_parser_test("42", source, expected)

# def test_43():
#     source = "struct Empty{" \
#              "};"
#     expected = "success"
#     run_parser_test("43", source, expected)

# def test_44():
#      source = "struct Cat{" \
#               "  string name;" \
#               "};" \
#               "void main(){Cat moew;}"
#      expected = "success"
#      run_parser_test("44", source, expected)
    
# def test_45():
#     source = "void f(){int y = 5;}" \
#              "struct Cat{" \
#              "  string name;" \
#              "};" \
#              "void main(){Cat moew;}"
#     expected = "success"
#     run_parser_test("45", source, expected)

# def test_46():
#     source = "void main(){ Point a = b; }"
#     expected = "success"
#     run_parser_test("46", source, expected)

# def test_47():
#     source = "void main(){ Point a = b; Point c; }"
#     expected = "success"
#     run_parser_test("47", source, expected)

# def test_48():
#     source = "void main(){ Domixi d = {\"kho ga\", \"alo Vu a?\"}; }"
#     expected = "success"
#     run_parser_test("48", source, expected)

# def test_49():
#     source = "void main(){ Vu v = {0, co, 3.14}; }"
#     expected = "success"
#     run_parser_test("49", source, expected)

# def test_50():
#     source = "void main(){ Cat c = {0}; }"
#     expected = "success"
#     run_parser_test("50", source, expected)

# def test_51():
#     source = "void main(){ Dog d = {}; }"
#     expected = "success"
#     run_parser_test("51", source, expected)

# def test_52():
#     source = "void main(){ Animal a = {1,}; }"
#     expected = "Error on line 1 col 27: }"
#     run_parser_test("52", source, expected)

# def test_53():
#     source = "void main(){ Error e = {; }"
#     expected = "Error on line 1 col 24: ;"
#     run_parser_test("53", source, expected)

# def test_54():
#     source = "void main(){ Constructor con{a, b, c}; }"
#     expected = "Error on line 1 col 28: {"
#     run_parser_test("54", source, expected)

# def test_55():
#     source = "void main(){ Error e = {status, message} }"
#     expected = "Error on line 1 col 41: }"
#     run_parser_test("55", source, expected)

# def test_56():
#     source = "void main(){ member.access = 5.5; }"
#     expected = "success"
#     run_parser_test("56", source, expected)

# def test_57():
#     source = "void main(){ not.assign; }"
#     expected = "success"
#     run_parser_test("57", source, expected)

# def test_58():
#     source = "void main(){ node.next.val; }"
#     expected = "success"
#     run_parser_test("58", source, expected)

# def test_59():
#     source = "void main(){ node.5.val }"
#     expected = "Error on line 1 col 17: .5"
#     run_parser_test("59", source, expected)

# def test_60():
#     source = "void main(){ cat.moew. }"
#     expected = "Error on line 1 col 23: }"
#     run_parser_test("60", source, expected)

# def test_61():
#     source = "int main(){" \
#              " int ac;" \
#              " }"
#     expected = "success"
#     run_parser_test("61", source, expected)

# def test_62():
#     source = "string main(int a){" \
#              " string s;" \
#              " }" \
#              "float num(float a){" \
#              " }"
#     expected = "success"
#     run_parser_test("62", source, expected)

# def test_63():
#     source = "void foo(int a, int b){}"
#     expected = "success"
#     run_parser_test("63", source, expected)

# def test_64():
#     source = "auto Domixi(int khoga){}"
#     expected = "Error on line 1 col 0: auto"
#     run_parser_test("64", source, expected)

# def test_65():
#     source = "no_return_type(int a, int b){ return a+b;}"
#     expected = "success"
#     run_parser_test("65", source, expected)

# def test_66():
#     source = "Node next(Node head){ return head.next;}"
#     expected = "success"
#     run_parser_test("66", source, expected)

# def test_67():
#     source = "no_auto_param(auto a){}"
#     expected = "Error on line 1 col 14: auto"
#     run_parser_test("67", source, expected)

# def test_68():
#     source = "no_param_after_comma(int a,){}"
#     expected = "Error on line 1 col 27: )"
#     run_parser_test("68", source, expected)

# def test_69():
#     source = "no_void_param(void here){}"
#     expected = "Error on line 1 col 14: void"
#     run_parser_test("69", source, expected)

# def test_70():
#     source = "no_default_param(int a = 5){}"
#     expected = "Error on line 1 col 23: ="
#     run_parser_test("70", source, expected)

# def test_71():
#     source = "no_type_id(a){}"
#     expected = "Error on line 1 col 12: )"
#     run_parser_test("71", source, expected)

# def test_72():
#     source = "int (int a){}"
#     expected = "Error on line 1 col 4: ("
#     run_parser_test("72", source, expected)

# def test_73():
#     source = "int no_block()"
#     expected = "Error on line 1 col 14: <EOF>"
#     run_parser_test("73", source, expected)

# def test_74():
#     source = "int a{ int a; }"
#     expected = "Error on line 1 col 5: {"
#     run_parser_test("74", source, expected)

# def test_75():
#     source = "struct_in_function(){ struct Point{ int a; int b;}; }"
#     expected = "Error on line 1 col 22: struct"
#     run_parser_test("75", source, expected)

# def test_76():
#     source = "add(5,7){}"
#     expected = "Error on line 1 col 4: 5"
#     run_parser_test("76", source, expected)

# def test_77():
#     source = "void main(){ function_call(); }"
#     expected = "success"
#     run_parser_test("77", source, expected)

# def test_78():
#     source = "void main(){ domixi_call(\"alo Vu a?\"); }"
#     expected = "success"
#     run_parser_test("78", source, expected)

# def test_79():
#     source = "void main(){ print(\"i luv u\", 0, 3.14, 1+2, b.c); }"
#     expected = "success"
#     run_parser_test("79", source, expected)

# def test_80():
#     source = "void main(){ error() }"
#     expected = "Error on line 1 col 21: }"
#     run_parser_test("80", source, expected)

# def test_81():
#     source = "void main(){ err(int a; }"
#     expected = "Error on line 1 col 17: int"
#     run_parser_test("81", source, expected)

# def test_82():
#     source = "void main(){ {" \
#              "  int a;" \
#              "  float pi = 3.14;" \
#              "}}"
#     expected = "success"
#     run_parser_test("82", source, expected)

# def test_83():
#     source = "void main(){ {" \
#              "  int a;" \
#              "}" \
#              "float pi = 3.14;}"
#     expected = "success"
#     run_parser_test("83", source, expected)

# def test_84():
#     source = "void main(){}"
#     expected = "success"
#     run_parser_test("84", source, expected)

# def test_85():
#     source = "void main(){ {int a; }"
#     expected = "Error on line 1 col 22: <EOF>"
#     run_parser_test("85", source, expected)

# def test_86():
#     source = "void main(){ string str;}}"
#     expected = "Error on line 1 col 25: }"
#     run_parser_test("86", source, expected)

# def test_87():
#     source = "func(){{}}"
#     expected = "success"
#     run_parser_test("87", source, expected)

# def test_88():
#     source = "void main(){ () }"
#     expected = "Error on line 1 col 14: )"
#     run_parser_test("88", source, expected)

# def test_89():
#     source = "void main(){ [] }"
#     expected = "Error Token ["
#     run_parser_test("89", source, expected)

# def test_90():
#     source = "void main(){ Node head = pre = node.next; }"
#     expected = "success"
#     run_parser_test("90", source, expected)

# def test_91():
#     source = "void main(){ int a = b + c; }"
#     expected = "success"
#     run_parser_test("91", source, expected)

# def test_92():
#     source = "void main(){ if(a == b){ print(\"ok\"); } }"
#     expected = "success"
#     run_parser_test("92", source, expected)

# def test_93():
#     source = "void main(){ if(uia == aiu) uia = aiu; else aiu = uia; }"
#     expected = "success"
#     run_parser_test("93", source, expected)

# def test_94():
#     source = "void main(){ if(condition){if(toiyeuem) toi = nho + em; else {em = nho + toi;} } }"
#     expected = "success"
#     run_parser_test("94", source, expected)

# def test_95():
#     source = "void main(){ else cond = whynotif; }"
#     expected = "Error on line 1 col 13: else"
#     run_parser_test("95", source, expected)

# def test_96():
#     source = "void main(){ if(a = 5){} }"
#     expected = "success"
#     run_parser_test("96", source, expected)

# def test_97():
#     source = "void main(){ if(str;) }"
#     expected = "Error on line 1 col 19: ;"
#     run_parser_test("97", source, expected)

# def test_98():
#     source = "void main(){ if(alo_Vu_a); }"
#     expected = "Error on line 1 col 25: ;"
#     run_parser_test("98", source, expected)

# def test_99():
#     source = "void main(){ if(khong_phai_anh_oi); else; }"
#     expected = "Error on line 1 col 34: ;"
#     run_parser_test("99", source, expected)

# def test_100():
#     source = "void main(){ if(tc_100 int holysheet; }"
#     expected = "Error on line 1 col 23: int"
#     run_parser_test("100", source, expected)

# def test_101():
#     source = "void main(){ if(100) { i_luv_u; }"
#     expected = "Error on line 1 col 33: <EOF>"
#     run_parser_test("101", source, expected)

# def test_102():
#     source = "void main(){ if(100) print(hello); print(world); else print(moew); }"
#     expected = "Error on line 1 col 49: else"
#     run_parser_test("102", source, expected)

# def test_103():
#     source = "void main(){ if(100){ print(hello); print(world); } else{ print(moew); print(moew); } }"
#     expected = "success"
#     run_parser_test("103", source, expected)

# def test_104():
#     source = "void main(){ if(1) int a; else int b; else int c; }"
#     expected = "Error on line 1 col 38: else"
#     run_parser_test("104", source, expected)

# def test_105():
#     source = "void main(){ if(int a = 5) print(ok); }"
#     expected = "Error on line 1 col 16: int"
#     run_parser_test("105", source, expected)

# def test_106():
#     source = "void main(){ if(a, b); }"
#     expected = "Error on line 1 col 17: ,"
#     run_parser_test("106", source, expected)

# def test_107():
#     source = "void main(){ if() print(err); }"
#     expected = "Error on line 1 col 16: )"
#     run_parser_test("107", source, expected)

# def test_108():
#     source = "void main(){ if print(moew); }"
#     expected = "Error on line 1 col 16: print"
#     run_parser_test("108", source, expected)

# def test_109():
#     source = "void main(){ while(true){ print(i_luv_u); } }"
#     expected = "success"
#     run_parser_test("109", source, expected)

# def test_110():
#     source = "void main(){ auto i = 0; while (i < 10) { printInt(i); ++i;} }"
#     expected = "success"
#     run_parser_test("110", source, expected)

# def test_111():
#     source = "void main(){ while(i_miss_u) print(moew); }"
#     expected = "success"
#     run_parser_test("111", source, expected)

# def test_112():
#     source = "void main(){ while(no_thing); }"
#     expected = "Error on line 1 col 28: ;"
#     run_parser_test("112", source, expected)

# def test_113():
#     source = "void main(){ while(no_statement_in_block){} }"
#     expected = "success"
#     run_parser_test("113", source, expected)

# def test_114():
#     source = "void main(){ while(err{} }"
#     expected = "Error on line 1 col 22: {"
#     run_parser_test("114", source, expected)

# def test_115():
#     source = "void main(){ while(err)} }"
#     expected = "Error on line 1 col 23: }"
#     run_parser_test("115", source, expected)

# def test_116():
#     source = "void main(){ while(1);{} }"
#     expected = "Error on line 1 col 21: ;"
#     run_parser_test("116", source, expected)

# def test_117():
#     source = "void main(){ while err print(err); }"
#     expected = "Error on line 1 col 19: err"
#     run_parser_test("117", source, expected)

# def test_118():
#     source = "void main(){ for(int i = 0; i < 10; ++i) { print(here); print(we); } }"
#     expected = "success"
#     run_parser_test("118", source, expected)

# def test_119():
#     source = "void main(){ for(i = 1; i > 10; i = i + 1) print(go); }"
#     expected = "success"
#     run_parser_test("119", source, expected)

# def test_120():
#     source = "void main(){ int i = 0; for(; i < size(); i = i++); }"
#     expected = "Error on line 1 col 50: ;"
#     run_parser_test("120", source, expected)

# def test_121():
#     source = "void main(){ int i = 10; for(;;i--) if(i == 0) break; else continue; }"
#     expected = "success"
#     run_parser_test("121", source, expected)

# def test_122():
#     source = "void main(){ for(;;) if(1) int a; else int b; }"
#     expected = "success"
#     run_parser_test("122", source, expected)

# def test_123():
#     source = "void main(){ for(int i;) print(i); }"
#     expected = "Error on line 1 col 23: )"
#     run_parser_test("123", source, expected)

# def test_124():
#     source = "void main(){ for() print(err); }"
#     expected = "Error on line 1 col 17: )"
#     run_parser_test("124", source, expected)

# def test_125():
#     source = "void main(){ for(a = a + b; true; false) break; }"
#     expected = "Error on line 1 col 39: )"
#     run_parser_test("125", source, expected)

# def test_126():
#     source = "void main(){ for(int i;i<s;i++ print(err); }"
#     expected = "Error on line 1 col 31: print"
#     run_parser_test("126", source, expected)

# def test_127():
#     source = "void main(){ for(;;;); }"
#     expected = "Error on line 1 col 19: ;"
#     run_parser_test("127", source, expected)

# def test_128():
#     source = "void main(){ for(;;) }"
#     expected = "Error on line 1 col 21: }"
#     run_parser_test("128", source, expected)

# def test_129():
#     source = "void main(){ while(true) }"
#     expected = "Error on line 1 col 25: }"
#     run_parser_test("129", source, expected)

# def test_130():
#     source = "void main(){ break; continue; }"
#     expected = "success"
#     run_parser_test("130", source, expected)

# def test_131():
#     source = "void main(){ while(1){{}} for(;;){{}} }"
#     expected = "success"
#     run_parser_test("131", source, expected)

# def test_132():
#     source = "void main(){ switch(enum){ case 1: print(ok); break; case 2: print(i_luv_u); default: break;} }"
#     expected = "success"
#     run_parser_test("132", source, expected)

# def test_133():
#     source = "void main(){ switch(1){ case 0: ; default: ;} }"
#     expected = "Error on line 1 col 32: ;"
#     run_parser_test("133", source, expected)

# def test_134():
#     source = "void main(){ switch(1){ default: {} } }"
#     expected = "success"
#     run_parser_test("134", source, expected)

# def test_135():
#     source = "void main(){ switch(1){ case 1: break; } }"
#     expected = "success"
#     run_parser_test("135", source, expected)

# def test_136():
#     source = "void main(){ switch(no_err){}}"
#     expected = "success"
#     run_parser_test("136", source, expected)

# def test_137():
#     source = "void main(){ switch(no_err){ default: break; case 1: hmm;}}"
#     expected = "success"
#     run_parser_test("137", source, expected)

# def test_138():
#     source = "void main(){ switch(err){ case : break; }}"
#     expected = "Error on line 1 col 31: :"
#     run_parser_test("138", source, expected)

# def test_139():
#     source = "void main(){ switch(err){ default break;} }"
#     expected = "Error on line 1 col 34: break"
#     run_parser_test("139", source, expected)

# def test_140():
#     source = "void main(){ switch(1){ default 1: ;}}"
#     expected = "Error on line 1 col 32: 1"
#     run_parser_test("140", source, expected)

# def test_141():
#     source = "void main(){ switch(1){ case 1:: break; }}"
#     expected = "Error on line 1 col 31: :"
#     run_parser_test("141", source, expected)

# def test_142():
#     source = "void main(){ switch(1){ 1: break;}}"
#     expected = "Error on line 1 col 24: 1"
#     run_parser_test("142", source, expected)

# def test_143():
#     source = "void main(){ switch(1) case 1: break;}"
#     expected = "Error on line 1 col 23: case"
#     run_parser_test("143", source, expected)

# def test_144():
#     source = "void main(){ switch 1 default: break;}"
#     expected = "Error on line 1 col 20: 1"
#     run_parser_test("144", source, expected)

# def test_145():
#     source = "void main(){ switch(1);}"
#     expected = "Error on line 1 col 22: ;"
#     run_parser_test("145", source, expected)

# def test_146():
#     source = "void main(){ switch(1)}"
#     expected = "Error on line 1 col 22: }"
#     run_parser_test("146", source, expected)

# def test_147():
#     source = "void main(){ switch(){}}"
#     expected = "Error on line 1 col 20: )"
#     run_parser_test("147", source, expected)

# def test_148():
#     source = "void main(){ switch(true, false){}}"
#     expected = "Error on line 1 col 24: ,"
#     run_parser_test("148", source, expected)

# def test_149():
#     source = "void main(){ switch(true;){}}"
#     expected = "Error on line 1 col 24: ;"
#     run_parser_test("149", source, expected)

# def test_150():
#     source = "void main(){ switch(){; }"
#     expected = "Error on line 1 col 20: )"
#     run_parser_test("150", source, expected)

# def test_151():
#     source = "void main(){ switch(1){ case 1,2: ;} }"
#     expected = "Error on line 1 col 30: ,"
#     run_parser_test("151", source, expected)

# def test_152():
#     source = "int main(){ return a; }"
#     expected = "success"
#     run_parser_test("152", source, expected)

# def test_153():
#     source = "void main(){ return;}"
#     expected = "success"
#     run_parser_test("153", source, expected)

# def test_154():
#     source = "int main(){ return };"
#     expected = "Error on line 1 col 19: }"
#     run_parser_test("154", source, expected)

# def test_155():
#     source = "int main(){ return a, b;}"
#     expected = "Error on line 1 col 20: ,"
#     run_parser_test("155", source, expected)

# def test_156():
#     source = "void main(){ x + y; }"
#     expected = "success"
#     run_parser_test("156", source, expected)

# def test_157():
#     source = "void main(){ ; }"
#     expected = "Error on line 1 col 13: ;"
#     run_parser_test("157", source, expected)

# def test_158():
#     source = "void main(){ 1;}"
#     expected = "success"
#     run_parser_test("158", source, expected)

# def test_159():
#     source = "void main(){ int a = b = c; }"
#     expected = "success"
#     run_parser_test("159", source, expected)

# def test_160():
#     source = "void main(){ int a = b = 2;}"
#     expected = "success"
#     run_parser_test("160", source, expected)

# def test_161():
#     source = "void main(){ a = b = c; }"
#     expected = "success"
#     run_parser_test("161", source, expected)

# def test_162():
#     source = "void main(){ int a = b * c;}"
#     expected = "success"
#     run_parser_test("162", source, expected)

# def test_163():
#     source = "void main(){ int a = a - b;}"
#     expected = "success"
#     run_parser_test("163", source, expected)

# def test_164():
#     source = "void main(){ int a = a / b; }"
#     expected = "success"
#     run_parser_test("164", source, expected)

# def test_165():
#     source = "void main(){ int a = a % 6; float pi = 3.14 / 1.0; }"
#     expected = "success"
#     run_parser_test("165", source, expected)

# def test_166():
#     source = "void main(){ a = b =; }"
#     expected = "Error on line 1 col 20: ;"
#     run_parser_test("166", source, expected)

# def test_167():
#     source = "void main(){ a = b = 2 }"
#     expected = "Error on line 1 col 23: }"
#     run_parser_test("167", source, expected)

# def test_168():
#     source = "void main(){ int a = a && b; }"
#     expected = "success"
#     run_parser_test("168", source, expected)

# def test_169():
#     source = "void main(){ int a = a || b; }"
#     expected = "success"
#     run_parser_test("169", source, expected)

# def test_170():
#     source = "void main(){ a == b; }"
#     expected = "success"
#     run_parser_test("170", source, expected)

# def test_171():
#     source = "void main(){ a != b; }"
#     expected = "success"
#     run_parser_test("171", source, expected)

# def test_172():
#     source = "void main(){ a || u != a && c == b; }"
#     expected = "success"
#     run_parser_test("172", source, expected)

# def test_173():
#     source = "void main(){ a && || b; }"
#     expected = "Error on line 1 col 18: ||"
#     run_parser_test("173", source, expected)

# def test_174():
#     source = "void main(){ a && b ||; }"
#     expected = "Error on line 1 col 22: ;"
#     run_parser_test("174", source, expected)

# def test_175():
#     source = "void main(){ && a; }"
#     expected = "Error on line 1 col 13: &&"
#     run_parser_test("175", source, expected)

# def test_176():
#     source = "void main(){ || a; }"
#     expected = "Error on line 1 col 13: ||"
#     run_parser_test("176", source, expected)

# def test_177():
#     source = "void main(){ a < b && a > b || c <= d && x >= y; }"
#     expected = "success"
#     run_parser_test("177", source, expected)

# def test_178():
#     source = "void main(){ > b;}"
#     expected = "Error on line 1 col 13: >"
#     run_parser_test("178", source, expected)

# def test_179():
#     source = "void main(){ a < ;}"
#     expected = "Error on line 1 col 17: ;"
#     run_parser_test("179", source, expected)

# def test_180():
#     source = "void main(){ a <= && b;}"
#     expected = "Error on line 1 col 18: &&"
#     run_parser_test("180", source, expected)

# def test_181():
#     source = "void main(){ (a &&) = b ||; }"
#     expected = "Error on line 1 col 18: )"
#     run_parser_test("181", source, expected)

# def test_182():
#     source = "void main(){ a + b + c - a; }"
#     expected = "success"
#     run_parser_test("182", source, expected)

# def test_183():
#     source = "void main(){ a -; }"
#     expected = "Error on line 1 col 16: ;"
#     run_parser_test("183", source, expected)

# def test_184():
#     source = "void main(){ a * b / c % d;}"
#     expected = "success"
#     run_parser_test("184", source, expected)

# def test_185():
#     source = "void main(){ * b;}"
#     expected = "Error on line 1 col 13: *"
#     run_parser_test("185", source, expected)

# def test_186():
#     source = "void main(){ c % ;}"
#     expected = "Error on line 1 col 17: ;"
#     run_parser_test("186", source, expected)

# def test_187():
#     source = "void main(){ !abc && !1 || -2 && +36; }"
#     expected = "success"
#     run_parser_test("187", source, expected)

# def test_188():
#     source = "void main(){ ++a + --b;}"
#     expected = "success"
#     run_parser_test("188", source, expected)

# def test_189():
#     source = "void main(){ a++ + b--; }"
#     expected = "success"
#     run_parser_test("189", source, expected)

# def test_190():
#     source = "void main(){ ++a++; }"
#     expected = "success"
#     run_parser_test("190", source, expected)

# def test_191():
#     source = "void main(){ --a--; }"
#     expected = "success"
#     run_parser_test("191", source, expected)

# def test_192():
#     source = "void main(){ a.b; }"
#     expected = "success"
#     run_parser_test("192", source, expected)

# def test_193():
#     source = "void main(){ a.b.c; }"
#     expected = "success"
#     run_parser_test("193", source, expected)

# def test_194():
#     source = "void main(){ 1.x; }"
#     expected = "Error on line 1 col 15: x"
#     run_parser_test("194", source, expected)

# def test_195():
#     source = "void main(){ 1..x; }"
#     expected = "success"
#     run_parser_test("195", source, expected)

# def test_196():
#     source = "void main(){ 1.0.x; }"
#     expected = "success"
#     run_parser_test("196", source, expected)

# def test_197():
#     source = "void main(){ \"alo Vu a Vu?\".size; }"
#     expected = "success"
#     run_parser_test("197", source, expected)

# def test_198():
#     source = "void main(){ (x).b; (a.b).c; }"
#     expected = "success"
#     run_parser_test("198", source, expected)

# def test_199():
#     source = "void main(){ a.(c); }"
#     expected = "Error on line 1 col 15: ("
#     run_parser_test("199", source, expected)

# def test_200():
#     source = "void main(){ bravo(a, 1 + 2 - 3, \"uia\", ++i--).x; }"
#     expected = "success"
#     run_parser_test("200", source, expected)

# def test_201():
#     source = "void main(){ uia(int a); }"
#     expected = "Error on line 1 col 17: int"
#     run_parser_test("201", source, expected)

# def test_202():
#     source = "void main(){ uia(a = 5); }"
#     expected = "success"
#     run_parser_test("202", source, expected)

# def test_203():
#     source = "void main(){ Domixi(Kho ga kg); }"
#     expected = "Error on line 1 col 24: ga"
#     run_parser_test("203", source, expected)

# def test_204():
#     source = "void main(){ cat.moew(cat); }"
#     expected = "Error on line 1 col 21: ("
#     run_parser_test("204", source, expected)

# def test_205():
#     source = "void main(){ (function(a,b)); }"
#     expected = "success"
#     run_parser_test("205", source, expected)

# def test_206():
#     source = "void main(){ --func()++; }"
#     expected = "success"
#     run_parser_test("206", source, expected)

# def test_207():
#     source = "void main(){ Do mixi = {Vu(), --ga, {alo, Vu, a}, {}}; }"
#     expected = "success"
#     run_parser_test("207", source, expected)

# def test_208():
#     source = "void main(){ {Error, err, e}; }"
#     expected = "success"
#     run_parser_test("208", source, expected)

# def test_209():
#     source = "void main(){ Error e = {print();}; }"
#     expected = "Error on line 1 col 31: ;"
#     run_parser_test("209", source, expected)

# def test_210():
#     source = "void main(){ INTEGER i = 1; }"
#     expected = "success"
#     run_parser_test("210", source, expected)

# def test_211():
#     source = "void main(){ E e = {status, message}.e; }"
#     expected = "success"
#     run_parser_test("211", source, expected)

# def test_212():
#     source = "void main(){ Empty empty = {{}, {}}; }"
#     expected = "success"
#     run_parser_test("212", source, expected)

# def test_213():
#     source = "void main(){ int a = {1, 2}; }" 
#     expected = "success"
#     run_parser_test("213", source, expected)

# def test_214():
#     source = """
#     int main(int argc, char argv){
#         Point p;
#         p.x = 1;
#         p.y = 2;
#         auto pp = p;
#         for(int i = startPoint({p.x, p.y}); endPoint(p, i); i = i + 1){
#             Point a = {p.x, p.y};
#             if(a.x == p - pp != 0 && a.y != p || pp){
#                 while(true){
#                     print(pp);
#                     switch(pp.y){
#                         case pp.toInt: 
#                             break;
#                         default:
#                             continue;
#                     }
#                 }
#             }
#         }
#     }
#     """
#     expected = "success"
#     run_parser_test("214", source, expected)

# def test_215():
#     source = "void main(){ for(Point a = {1, 2}; a.x < 2 && a.y == 2; a.x++) print(a); }"
#     expected = "success"
#     run_parser_test("215", source, expected)

# def test_216():
#     source = "void main(){ Point p; p = {1,2}; }"
#     expected = "success"
#     run_parser_test("216", source, expected)

# def test_217():
#     source = "main(){ main(); }"
#     expected = "success"
#     run_parser_test("217", source, expected)

# def test_218():
#     source = "main(){ main(){} }"
#     expected = "Error on line 1 col 14: {"
#     run_parser_test("218", source, expected)

# def test_219():
#     source = "main(){ struct Point{}; }"
#     expected = "Error on line 1 col 8: struct"
#     run_parser_test("219", source, expected)

# def test_220():
#     source = "void main(){ int a = (int); }"
#     expected = "Error on line 1 col 22: int"
#     run_parser_test("220", source, expected)

# def test_221():
#     source = "void main(){ (int a); }"
#     expected = "Error on line 1 col 14: int"
#     run_parser_test("221", source, expected)

# def test_222():
#     source = "void main(){ c = (a = b); }"
#     expected = "success"
#     run_parser_test("222", source, expected)

# def test_223():
#     source = "void main(){ recursion(recursion()); }"
#     expected = "success"
#     run_parser_test("223", source, expected)

# def test_224():
#     source = "void main(){ check(a,); }"
#     expected = "Error on line 1 col 21: )"
#     run_parser_test("224", source, expected)

# def test_225():
#     source = "void main(){ print(toi yeu em); }"
#     expected = "Error on line 1 col 23: yeu"
#     run_parser_test("225", source, expected)

# def test_226():
#     source = "int a = 5;"
#     expected = "Error on line 1 col 6: ="
#     run_parser_test("226", source, expected)

# def test_227():
#     source = "a = 5;"
#     expected = "Error on line 1 col 2: ="
#     run_parser_test("227", source, expected)

# def test_228():
#     source = "void main(){ for(int i = 0; i < 0; i++++){} }"
#     expected = "success"
#     run_parser_test("228", source, expected)

# def test_229():
#     source = "void main(){ for(int i = 0; i < 0; --(--i)){} }"
#     expected = "success"
#     run_parser_test("229", source, expected)

# def test_230():
#     source = "void main(){ foo({2,3}, 1, {}, {{2}, 3});}"
#     expected = "success"
#     run_parser_test("230", source, expected)

"""
Parser test cases for TyC compiler
TODO: Implement 100 test cases for parser
"""

import string
import pytest
from tests.utils import Parser
import os

"""
Parser test cases for TyC compiler
Each test_* function represents ONE test case.
Expected output is embedded directly in code.
Actual output is written to .txt file per test.
"""

# BASE_DIR = os.path.dirname(__file__)
# OUTPUT_DIR = os.path.join(BASE_DIR, "output", "parser")

def run_parser_test(test_name: str, source: str, expected: str, n_match: bool = False):
    parser = Parser(source)
    output = parser.parse()

    # # Write output to file
    # output_path = os.path.join(OUTPUT_DIR, f"{test_name}.txt")
    # with open(output_path, "w", encoding="utf-8") as f:
    #     f.write(output)

    assert output == expected, f"Output: {output}. Expected: {expected}"

"""
1 - 15 Declaration (Var and Struct)
16 - 21 Switch
22 - 30 For loop 
31 - 45 Assignment Expression
46 - 55 If Else
56 - 69 Function decl, Function call
70 - 105 Free-For-All (AI gen)
"""

def test_1():
    source = """
    void main(){
        int a;
    }
    """
    expected = "success"
    run_parser_test("1", source, expected)

def test_2():
    source = """
    void main(){
    Person person2 = {\"John\", 25, 1.75, {}};
    return 0;
    }
    """
    expected = "success"
    run_parser_test("2", source, expected)

def test_3():
    source = """
    void main(){
    Person person2 = {Point p2 = {10, 20},  25, 1.75};
    }
    """
    expected = "Error on line 3 col 28: p2"
    run_parser_test("3", source, expected)

def test_4():
    source = """
    void main(){
    Person person2 = {};
    }
    """
    expected = "success"
    run_parser_test("4", source, expected)

def test_5():
    source = """
    void main(){
    Person person2 = {a.x = ++jk(kratos)};
    }
    """
    expected = "success"
    run_parser_test("5", source, expected)

def test_6():
    source = """
    void main(){
    Person person2 = {p2, 1, "let's go"};
    }
    """
    expected = "success"
    run_parser_test("6", source, expected)  

def test_7():
    source = """
    struct A {
        int Jah;
        struct B {
            int x;
        };
    };
    """
    expected = "Error on line 4 col 8: struct"
    run_parser_test("7", source, expected)  

def test_8():
    source = """
    struct A {
        int a;
        int b;
        void YhICameInWitheTheSauce(int jeffery, int epstein){
            a = jeffery;
            b = epstein;
        }
    }
    void main() {}
    """
    expected = "Error on line 5 col 8: void"
    run_parser_test("8", source, expected)  

def test_9():
    source = """
    void main(){
    A aa = {"string", 1, {}};
    }
    """
    expected = "success"
    run_parser_test("9", source, expected)  

def test_10():
    source = """
    void main(){
    int a = y = z = c = 10;
    }
    """
    expected = "success"
    run_parser_test("10", source, expected) 
    
def test_11():
    source = "struct Empty {};  // Valid: empty struct with no members"
    expected = "success"
    run_parser_test("10", source, expected) 

def test_12():
    source = """
    void main(){
    int a = ++10-- a;
    }
    """
    expected = "Error on line 3 col 19: a"
    run_parser_test("12", source, expected) 

def test_13():
    source = """
    int main(){
    int a = BroSki() + ++a/4;
    return 0;
    }
    """
    expected = "success"
    run_parser_test("13", source, expected) 

def test_14():
    source = """
    void main(){
    int a = BroSki() + (Jawohl).x;
    return 0;
    }
    """
    expected = "success"
    run_parser_test("14", source, expected) 

def test_15():
    source = """
    void main(){
    int a,b,c = 10;
    return;
    }
    """
    expected = "Error on line 3 col 9: ,"
    run_parser_test("15", source, expected) 

def test_16():
    source = """
    void main(){
        switch (x) {
                default:
                    printInt(0);
                case 1:
                    printInt(1);
            }
    return;
    }
    """
    expected = "success"
    run_parser_test("16", source, expected) 

def test_17():
    source = """
    void main(){
        switch (a.b + ++g - foo()) {
            case 1:
                printInt(1);
            default:
                printInt(0);
            case 1:
                printInt(1);
        }
    return;
    }
    """
    expected = "success"
    run_parser_test("17", source, expected) 

def test_18():
    source = """
    void main(){
        switch (a.b + ++g - foo()) {
            case 1 + 2 * (3 - 1):
                printInt(1);
            default:
                functionHere() + foo();
            case 1:
                printInt(1);
        }
    return;
    }
    """
    expected = "success"
    run_parser_test("18", source, expected) 

def test_19():
    source = """
    void main(){
        switch () {
            case 1 + 2 * (3 - 1):
                printInt(1);
            default:
                ;
        }
        return;
    }
            """
    expected = "Error on line 2 col 16: )"
    run_parser_test("19", source, expected) 

def test_19():
    source = """
    int Foo(){
        switch (a || b + ++c / foo()) {
            case 1 + 2 * (3 - 1):
                printInt(1);
            default:
                ;
        }
    }
            """
    expected = "Error on line 6 col 16: ;"
    run_parser_test("19", source, expected) 

def test_19():
    source = """
    void main(){
        switch (a) {
            case 1 + 2 * (3 - 1):
                ;
            default:
                ;
        }
        return;
    }
            """
    expected = "Error on line 5 col 16: ;"
    run_parser_test("19", source, expected) 

def test_20():
    source = """
    void main(){
        switch (a) {
            case 1 + 2 * (3 - 1):
                break;
        }
    return;
    }
            """
    expected = "success"
    run_parser_test("19", source, expected) 

def test_21():
    source = """
    void main(){
        switch (x) { }
    return 0;
    }
            """
    expected = "success"
    run_parser_test("21", source, expected) 

def test_22():
    source = """
    int Sunmo(int a, int b){
        int i;
        for (i = 0; i < n; ){}
    }
            """
    expected = "success"
    run_parser_test("22", source, expected) 

def test_23():
    source = """
    T14 Shiff(int g){
        int i;
        for (; i < (n); ){}
    return g;
    }
            """
    expected = "success"
    run_parser_test("23", source, expected) 

def test_24():
    source = """
    void main(){
        auto i;
        for (; i != foo(a) ; ){}
        return 0;
    }
            """
    expected = "success"
    run_parser_test("24", source, expected) 

def test_25():
    source = """
    void bgh(){
        auto i;
        for (; (i) < sum(a+b) ; --i){}
    return;
    }
            """
    expected = "success"
    run_parser_test("25", source, expected) 
    
def test_26():
    source = """
    float Nig(float b){
        auto i;
        for (i == 0; i < nibba; i++){}
        return 3.14;
    }
            """
    expected = "Error on line 4 col 15: =="
    run_parser_test("26", source, expected) 

def test_27():
    source = """
    void Conduct(){
        auto i;
        for (i = 0; true; i++){
            printf("%d",1);
        }
    return;
    }
            """
    expected = "success"
    run_parser_test("27", source, expected) 

def test_28():
    source = """
    int main(){
        auto i;
        for (i = 0; true; i++) conCho cao = {"Do", "Skibid", {"Tay",67}};
        return 0;
    }
            """
    expected = "success"
    run_parser_test("28", source, expected)

def test_29():
    source = """
    void for(){
        auto i;
        for (i = 0; true; i++){
        choDo();
        void muHaHa(){
            return;
            }
        }
    }
        """
    expected = "Error on line 2 col 9: for"
    run_parser_test("29", source, expected)

def test_30():
    source = """
    int main(){
        auto i;
        for (c cc = {1,2}; (cc).a < 10; cc.a++){
            printf("%d",1);
            cc.(a)++
        }
    }
        """
    expected = "Error on line 6 col 15: ("
    run_parser_test("30", source, expected)

def test_31():
    source = """
    void main(){
        auto x = a.c + ((fubar()) / ++y);
        return 0;
    }
        """
    expected = "success"
    run_parser_test("31", source, expected)

def test_32():
    source = """
    void main(){
        auto x = a.c + ((fubar()) / ++y) && (!j);
        }
        """
    expected = "success"
    run_parser_test("32", source, expected)

def test_33():
    source = """
    void main(){
        foo().a = 1;
        }
        """
    expected = "success"
    run_parser_test("33", source, expected)

def test_34():
    source = """
    void main(){
        auto x = ++a.b.c;
        }
        """
    expected = "success"
    run_parser_test("34", source, expected)

def test_35():
    source = """
    void main(){
        auto x = g({{1,2},3});
        }
        """
    expected = "success"
    run_parser_test("35", source, expected)

def test_36():
    source = """
    void main(){
        auto x = g({{1,2},3}, {}, g() + 1);
        }
        """
    expected = "success"
    run_parser_test("36", source, expected)

def test_37():
    source = """
    void main(){
        auto x = g({{1,2},3}, {}, g() + 1);
        }
        """
    expected = "success"
    run_parser_test("37", source, expected)
    
def test_38():
    source = """
    void main(){
        auto a = b = c + d;
        }
        """
    expected = "success"
    run_parser_test("38", source, expected)

def test_39():
    source = """
    int x = 10;
        """
    expected = "Error on line 2 col 10: ="
    run_parser_test("39", source, expected)

def test_40():
    source = """
    void main(){
        auto a = a < b == c < d;
        }
        """
    expected = "success"
    run_parser_test("40", source, expected)

def test_41():
    source = """
    void main(){
        int x = (a + b;
        }
        """
    expected = "Error on line 3 col 22: ;"
    run_parser_test("41", source, expected)

def test_42():
    source = """
    void main(){
    // here right ?
        auto x = (a + b) = c;
    }
    """
    expected = "Error on line 4 col 25: ="
    run_parser_test("42", source, expected)

def test_43():
    source = """
    void main(){
        auto x = a.x = c || b;
    }
    """
    expected = "success"
    run_parser_test("43", source, expected)

def test_44():
    source = """
    void main(){
        auto (x) = (a).x = c || b;
    }
    """
    expected = "Error on line 3 col 13: ("
    run_parser_test("44", source, expected)

def test_45():
    source = """
    void main(){
        auto x = ((a).x = (c || b));
    }
    """
    expected = "success"
    run_parser_test("45", source, expected)

def test_46():
    source = """
    void main(){
        if (flag) {
            printInt(1);
        } else {
            printInt(0);
}
    }
    """
    expected = "success"
    run_parser_test("46", source, expected)

def test_47():
    source = """
    void main(){
        else {
            printInt(0);
        }
    }
    """
    expected = "Error on line 3 col 8: else"
    run_parser_test("47", source, expected)

def test_48():
    source = """
    void main(){
        if (a)
            x = 1;
        else {
            x = 2;
            y = 3;
        }   
    }
    """
    expected = "success"
    run_parser_test("48", source, expected)

def test_49():
    source = """
    void main(){
        if (true)
            x = 1;
        else {
            x = 2;
            y = 3;
        }   
    }
    """
    expected = "success"
    run_parser_test("49", source, expected)

def test_50():
    source = """
    void main(){
        if (a);
    }
    """
    expected = "Error on line 3 col 14: ;"
    run_parser_test("50", source, expected)

def test_51():
    source = """
    void main(){
        for (i = 0; i < 10; i++)
            if (i % 2)
                x = i;
            else
                y = i;
    }
    """
    expected = "success"
    run_parser_test("51", source, expected)

def test_52():
    source = """
    void main(){
        if (x = y + 1)
            z = 2;
    }
    """
    expected = "success"
    run_parser_test("52", source, expected)

def test_53():
    source = """
    void main(){
        if (a)
            if (b)
                if (c)
                    x = 1;
                else
                    x = 2;
    }
    """
    expected = "success"
    run_parser_test("53", source, expected)

def test_54():
    source = """
    void main(){
        if (a){
            return 0;
            return;
        }
        else
            continue;
    return; 
    }
    """
    expected = "success"
    run_parser_test("54", source, expected)

def test_55():
    source = """
    void main(){
        if (a)
            return 0;
            return;
        else
            continue;
            return; 
    }
    """
    expected = "Error on line 6 col 8: else"
    run_parser_test("55", source, expected)

def test_56():
    source = """
    """
    expected = "success"
    run_parser_test("56", source, expected)

def test_56():
    source = """
        void main() {
            int f(int x) {
            return x;
            }
        }
    """
    expected = "Error on line 3 col 17: ("
    run_parser_test("56", source, expected)

def test_57():
    source = """
        int f() {
            return 1;
            return 2;
        }
    """
    expected = "success"
    run_parser_test("57", source, expected)

def test_58():
    source = """
        int f() {
            return 1;
            return 2;
        }
    """
    expected = "success"
    run_parser_test("58", source, expected)

def test_59():
    source = """
        void void() {
            return 1;
            return 2;
        }
    """
    expected = "Error on line 2 col 13: void"
    run_parser_test("59", source, expected)

def test_60():
    source = """
        void sum(int a, int b, int c) {
            auto y = f(a) + f(b) * (f(c));
        }
    """
    expected = "success"
    run_parser_test("60", source, expected)

def test_61():
    source = """
        void sum(int a, int b, int c) {
            auto y = f(a) + f(b) * (f(c));
            return "Y-Que-Fue?";
        }
    """
    expected = "success"
    run_parser_test("61", source, expected)

def test_62():
    source = """
        void sum(int a,b) {
            auto y = f(a) + f(b) * (f(c));
            return "Y-Que-Fue?";
        }
    """
    expected = "Error on line 2 col 24: )"
    run_parser_test("62", source, expected)

def test_62():
    source = """
        void sum(int a,b) {
            auto y = f(a) + f(b) * (f(c));
            return "Y-Que-Fue?";
        }
    """
    expected = "Error on line 2 col 24: )"
    run_parser_test("62", source, expected)

def test_63():
    source = """
        void main(){ 
            int x = f(a, g(b)); 
        }
    """
    expected = "success"
    run_parser_test("63", source, expected)

def test_64():
    source = """
        foo(){
            for(int i = 0; i < 10; foo(i)++){
                FAH().x = 1;
            }
            for(int i = 0; i < 10; foo(i)){
                FAH().x = 1;
            }
        }
        void main(){ 
            foo();
        }
    """
    expected = "Error on line 6 col 41: )"
    run_parser_test("64", source, expected)

def test_65():
    source = """
        void main(){ 
            int x = f(a, g(b), {4,5}, {}); 
        }
    """
    expected = "success"
    run_parser_test("65", source, expected)

def test_66():
    source = """
        void main(){ 
            x.y = f(a, g(b), {4,5}, {}); 
        }
    """
    expected = "success"
    run_parser_test("66", source, expected)

def test_67():
    source = """
        void main(){ 
            foo()++;
        }
    """
    expected = "success"
    run_parser_test("67", source, expected)

def test_68():
    source = """
        void main(){ 
            int x = foo()++++ + i;
        }
    """
    expected = "success"
    run_parser_test("68", source, expected)

def test_69():
    source = """
        void fah(){
        for(; ep() < 9; a++){
                        {
                            while(a < 7) {
                                {
                                    switch(a){
                                        {
                                        
                                        }
                                    }
                                }
                            }   
                        }
                    }
        }
        void main(){ 
            fah();
        }
    """
    expected = "Error on line 8 col 40: {"
    run_parser_test("69", source, expected)

def test_70():
    source = """
    void main(){
        int i = 0;
        for (i = 0; i < 10; i = i + 1) {
            if (i % 2 == 0)
                printInt(i);
        }
    }
    """
    expected = "success"
    run_parser_test("70", source, expected)

def test_71():
    source = """
    void main(){
        int x = 10;
        while (x > 0) {
            x = x - 1;
            if (x == 5)
                break;
        }
    }
    """
    expected = "success"
    run_parser_test("71", source, expected)

def test_72():
    source = """
    void main(){
        int a = 10;
        if (a > 5) {
            a = a + 1;
            break;
        }
    }
    """
    expected = "success"   # semantic mới lỗi
    run_parser_test("72", source, expected)

def test_73():
    source = """
    void main(){
        int x = 2;
        switch (x) {
            case 1:
                x = x + 1;
            case 2:
                x = x + 2;
                break;
            default:
                x = 0;
        }
    }
    """
    expected = "success"
    run_parser_test("73", source, expected)

def test_74():
    source = """
    void main(){
        int i = 0;
        for (i = 0; i < 5; i = i + 1) {
            int j = 0;
            while (j < 5) {
                j = j + 1;
                if (j == 3)
                    continue;
            }
        }
    }
    """
    expected = "success"
    run_parser_test("74", source, expected)

def test_75():
    source = """
    void main(){
        auto x = foo(1, 2) + bar(a, b) * (baz() - 3);
        printInt(x);
    }
    """
    expected = "success"
    run_parser_test("75", source, expected)

def test_76():
    source = """
    void main(){
        if (a)
            if (b)
                x = 1;
        else
            x = 2;
    }
    """
    expected = "success"
    run_parser_test("76", source, expected)

def test_77():
    source = """
    void main(){
        int x = 1;
        switch (x) {
            case 1:
                x = 2;
                break;
    }
    """
    expected = "Error on line 9 col 4: <EOF>"
    run_parser_test("77", source, expected)


def test_78():
    source = """
    void main(){
        int i = 0;
        for (i = 0 i < 10; i = i + 1) {
            printInt(i);
        }
    }
    """
    expected = "Error on line 4 col 19: i"
    run_parser_test("78", source, expected)

def test_79():
    source = """
    void main(){
        int i = 0;
        for (i = 0; i < 3; i = i + 1) {
            switch (i) {
                case 0:
                    foo();
                    break;
                case 1:
                    while (i < 2 && foo() != "ThatOneFlower") {
                        i = i + 1;
                    }
                    break;
                default:
                    bar(i);
            }
        }
    }
    """
    expected = "success"
    run_parser_test("79", source, expected)

def test_80():
    source = """
    void main(){
        for (auto i = 0; i < 3; i = i + 1) {
            switch (i) {
                case 0:
                    i = i + 1;
                case 1:
                    i = i + 2;
                    break;
                default:
                    i = 0;
            }
        }
    }
    """
    expected = "success"
    run_parser_test("80", source, expected)

def test_81():
    source = """
    void main(){
        while (foo(a + b * c)) {
            {
                auto x = bar(foo(1), (a = b));
                x = x + 1;
            }
        }
    }
    """
    expected = "success"
    run_parser_test("81", source, expected)

def test_82():
    source = """
    void main(){
        for (; ; (i)++) {
            switch ((a + b) * (c - d)) {
                case 1 + 2:
                    foo();
                case (3 * 4):
                    bar();
                    break;
                default:
                    baz();
            }
        }
    }
    """
    expected = "success"
    run_parser_test("82", source, expected)

def test_83():
    source = """
    void main(){
        auto x;
        auto y;
        auto z;
        x = y = z = foo(a, b + c);
    }
    """
    expected = "success"
    run_parser_test("83", source, expected)

def test_84():
    source = """
    void main(){
        if (a > b)
            switch (a) {
                case 1:
                    return;
                default:
                    return;
            }
        else
            return;
    }
    """
    expected = "success"
    run_parser_test("84", source, expected)

def test_85():
    source = """
    void main(){
        foo({1, 2, {3, 4}}, bar({5}));
    }
    """
    expected = "success"
    run_parser_test("85", source, expected)

def test_86():
    source = """
    void main(){
        while (a < b) {
            if (a == 0)
                continue;
            if (a > 10)
                break;
            a = a + 1;
        }
    }
    """
    expected = "success"
    run_parser_test("86", source, expected)

def test_87():
    source = """
    void main(){
        for (i == 1; i < k; ++i){
            GotCha("=))");
        }
    }
    """
    expected = "Error on line 3 col 15: =="
    run_parser_test("87", source, expected)

def test_88():
    source = """
    void main(){
        for (Point p = {1, 2}; p.x < 10; p.x = p.x + 1) {
            foo(p);
        }
    }
    """
    expected = "success"
    run_parser_test("88", source, expected)

def test_89():
    source = """
    void main(){
        switch (a + b) {
        }
    }
    """
    expected = "success"
    run_parser_test("89", source, expected)

def test_90():
    source = """
    void main(){
        switch (a + b {
            case 1: break;
        }
    }
    """
    expected = "Error on line 3 col 22: {"
    run_parser_test("90", source, expected)

def test_91():
    source = """
    void main(){
        switch (a) {
            case 1:
                break;
        }
    }
    """
    expected = "success"
    run_parser_test("91", source, expected)

def test_92():
    source = """
    void main(){
        for (auto i = 0 i < 10; i = i + 1) {
            foo();
        }
    }
    """
    expected = "Error on line 3 col 24: i"
    run_parser_test("92", source, expected)

def test_93():
    source = """
    void main(){
        while () {
            foo();
        }
    }
    """
    expected = "Error on line 3 col 15: )"
    run_parser_test("93", source, expected)

def test_94():
    source = """
    void main(){
        foo(1, 2;
    }
    """
    expected = "Error on line 3 col 16: ;"
    run_parser_test("94", source, expected)

def test_95():
    source = """
    void main(){
        a = ;
    }
    """
    expected = "Error on line 3 col 12: ;"
    run_parser_test("95", source, expected)

def test_96():
    source = """
    void main(){
        10++;
    }
    """
    expected = "success"
    run_parser_test("96", source, expected)

def test_97():
    source = """
    void main(){
        a.;
    }
    """
    expected = "Error on line 3 col 10: ;"
    run_parser_test("97", source, expected)

def test_98():
    source = """
    void main(){
        switch () {
            case 1: break;
        }
    }
    """
    expected = "Error on line 3 col 16: )"
    run_parser_test("98", source, expected)

def test_99():
    source = """
    void main(){
        for (i = 0; i < 10; ) ) {
            foo();
        }
    }
    """
    expected = "Error on line 3 col 30: )"
    run_parser_test("99", source, expected)

def test_100():
    source = """
    void main(){
        {1,2}.b;
    }
    """
    expected = "success"
    run_parser_test("100", source, expected)

def test_101():
    source = """
    main(a){
        int i = 1hellnah(a);
    }
    """
    expected = "Error on line 2 col 10: )"
    run_parser_test("101", source, expected)

def test_102():
    source = """
    void main(){
        int i = _1hellnah(a);
    }
    """
    expected = "success"
    run_parser_test("102", source, expected)

def test_103():
    source = """
    void main(){
        int i = 1 + ++a--++;
    }
    """
    expected = "success"
    run_parser_test("103", source, expected)

def test_104():
    source = """
    void main(){
        foo().a = 1;
        int a = foo().b;
        (foo()).c = 3;
    }
    """
    expected = "success"
    run_parser_test("103", source, expected)

def test_105():
    source = """
    void main(){
        inRa("you reached this point, congrat and goodluck.");
    }
    """
    expected = "success"
    run_parser_test("103", source, expected)
