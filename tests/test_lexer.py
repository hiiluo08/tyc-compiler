"""
Lexer test cases for TyC compiler
Comprehensive test suite covering all lexical elements
"""

import pytest
from tests.utils import Tokenizer


# ============================================================================
# COMMENT TESTS
# ============================================================================

# def test_001_block_comment():
#     """Test block comment - should be ignored"""
#     source = """\t\r
#     /* This is a block comment so // has no meaning here */
# """
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_002_line_comment():
#     """Test line comment - should be ignored"""
#     source = "// This is a line comment\n"
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_003_line_comment_no_newline():
#     """Test line comment ending at EOF"""
#     source = "// This is a line comment"
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_004_block_comment_multiline():
#     """Test multiline block comment"""
#     source = """/* This is a 
#     multiline
#     block comment */"""
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_005_line_comment_with_block_comment_chars():
#     """Test that /* has no meaning in line comment"""
#     source = "// This line comment has /* which means nothing\n"
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_006_mixed_comments_and_code():
#     """Test comments mixed with code"""
#     source = "int /* comment */ x // line comment"
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_007_multiple_line_comments():
#     """Test multiple consecutive line comments"""
#     source = """// Comment 1
# // Comment 2
# // Comment 3"""
#     expected = "EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # KEYWORD TESTS
# # ============================================================================

# def test_008_keyword_auto():
#     source = "auto"
#     expected = "auto,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_009_keyword_break():
#     source = "break"
#     expected = "break,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_010_keyword_case():
#     source = "case"
#     expected = "case,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_011_keyword_continue():
#     source = "continue"
#     expected = "continue,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_012_keyword_default():
#     source = "default"
#     expected = "default,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_013_keyword_else():
#     source = "else"
#     expected = "else,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_014_keyword_float():
#     source = "float"
#     expected = "float,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_015_keyword_for():
#     source = "for"
#     expected = "for,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_016_keyword_if():
#     source = "if"
#     expected = "if,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_017_keyword_int():
#     source = "int"
#     expected = "int,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_018_keyword_return():
#     source = "return"
#     expected = "return,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_019_keyword_string():
#     source = "string"
#     expected = "string,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_020_keyword_struct():
#     source = "struct"
#     expected = "struct,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_021_keyword_switch():
#     source = "switch"
#     expected = "switch,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_022_keyword_void():
#     source = "void"
#     expected = "void,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_023_keyword_while():
#     source = "while"
#     expected = "while,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_024_all_keywords():
#     """Test all keywords in one test"""
#     source = "auto break case continue default else float for if int return string struct switch void while"
#     expected = "auto,break,case,continue,default,else,float,for,if,int,return,string,struct,switch,void,while,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # IDENTIFIER TESTS
# # ============================================================================

# def test_025_identifier_simple():
#     source = "x"
#     expected = "x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_026_identifier_with_underscore():
#     source = "_variable"
#     expected = "_variable,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_027_identifier_with_digits():
#     source = "var123"
#     expected = "var123,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_028_identifier_camelCase():
#     source = "myVariable"
#     expected = "myVariable,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_029_identifier_PascalCase():
#     source = "MyVariable"
#     expected = "MyVariable,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_030_identifier_snake_case():
#     source = "my_variable_name"
#     expected = "my_variable_name,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_031_identifier_all_uppercase():
#     source = "CONSTANT"
#     expected = "CONSTANT,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_032_identifier_single_underscore():
#     source = "_"
#     expected = "_,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_033_identifier_multiple_underscores():
#     source = "__private__"
#     expected = "__private__,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_034_identifier_vs_keyword():
#     """Identifier that contains keyword but is not a keyword"""
#     source = "integer"
#     expected = "integer,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_035_identifier_multiple():
#     source = "x y z"
#     expected = "x,y,z,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # OPERATOR TESTS
# # ============================================================================

# def test_036_operator_plus():
#     source = "+"
#     expected = "+,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_037_operator_minus():
#     source = "-"
#     expected = "-,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_038_operator_multiply():
#     source = "*"
#     expected = "*,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_039_operator_divide():
#     source = "/"
#     expected = "/,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_040_operator_modulus():
#     source = "%"
#     expected = "%,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_041_operator_equal():
#     source = "=="
#     expected = "==,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_042_operator_not_equal():
#     source = "!="
#     expected = "!=,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_043_operator_less_than():
#     source = "<"
#     expected = "<,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_044_operator_greater_than():
#     source = ">"
#     expected = ">,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_045_operator_less_equal():
#     source = "<="
#     expected = "<=,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_046_operator_greater_equal():
#     source = ">="
#     expected = ">=,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_047_operator_logical_or():
#     source = "||"
#     expected = "||,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_048_operator_logical_and():
#     source = "&&"
#     expected = "&&,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_049_operator_logical_not():
#     source = "!"
#     expected = "!,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_050_operator_increment():
#     source = "++"
#     expected = "++,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_051_operator_decrement():
#     source = "--"
#     expected = "--,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_052_operator_assignment():
#     source = "="
#     expected = "=,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_053_operator_dot():
#     source = "."
#     expected = ".,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_054_operators_multiple():
#     """Test multiple operators together"""
#     source = "+ - * / %"
#     expected = "+,-,*,/,%,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_055_operators_comparison():
#     source = "< <= > >= == !="
#     expected = "<,<=,>,>=,==,!=,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_056_operators_logical():
#     source = "&& || !"
#     expected = "&&,||,!,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # SEPARATOR TESTS
# # ============================================================================

# def test_057_separator_left_brace():
#     source = "{"
#     expected = "{,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_058_separator_right_brace():
#     source = "}"
#     expected = "},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_059_separator_left_paren():
#     source = "("
#     expected = "(,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_060_separator_right_paren():
#     source = ")"
#     expected = "),EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_061_separator_semicolon():
#     source = ";"
#     expected = ";,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_062_separator_comma():
#     source = ","
#     expected = ",,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_063_separator_colon():
#     source = ":"
#     expected = ":,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_064_separators_all():
#     source = "{ } ( ) ; , :"
#     expected = "{,},(,),;,,,:,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # INTEGER LITERAL TESTS
# # ============================================================================

# def test_065_integer_zero():
#     source = "0"
#     expected = "0,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_066_integer_positive():
#     source = "42"
#     expected = "42,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_067_integer_large():
#     source = "123456789"
#     expected = "123456789,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_068_integer_negative():
#     """Negative sign is separate token"""
#     source = "-45"
#     expected = "-,45,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_069_integer_multiple():
#     source = "1 2 3"
#     expected = "1,2,3,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_070_integer_leading_zeros():
#     """Leading zeros are still valid decimal integers"""
#     source = "007"
#     expected = "007,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # FLOAT LITERAL TESTS
# # ============================================================================

# def test_071_float_with_decimal():
#     source = "3.14"
#     expected = "3.14,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_072_float_zero():
#     source = "0.0"
#     expected = "0.0,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_073_float_decimal_only():
#     source = ".5"
#     expected = ".5,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_074_float_integer_part_only():
#     source = "1."
#     expected = "1.,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_075_float_with_exponent():
#     source = "1.23e4"
#     expected = "1.23e4,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_076_float_exponent_uppercase():
#     source = "5.67E-2"
#     expected = "5.67E-2,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_077_float_exponent_positive():
#     source = "1.23e+4"
#     expected = "1.23e+4,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_078_float_exponent_no_decimal():
#     source = "1e4"
#     expected = "1e4,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_079_float_exponent_uppercase_no_decimal():
#     source = "2E-3"
#     expected = "2E-3,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_080_float_negative():
#     """Negative sign is separate token"""
#     source = "-3.14"
#     expected = "-,3.14,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_081_float_multiple():
#     source = "1.0 2.5 3.14"
#     expected = "1.0,2.5,3.14,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # STRING LITERAL TESTS
# # ============================================================================

# def test_082_string_simple():
#     source = '"hello"'
#     expected = 'hello,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_083_string_empty():
#     source = '""'
#     expected = ',EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_084_string_with_spaces():
#     source = '"hello world"'
#     expected = 'hello world,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_085_string_escape_tab():
#     source = '"tab\\there"'
#     expected = 'tab\\there,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_086_string_escape_newline():
#     source = '"line1\\nline2"'
#     expected = 'line1\\nline2,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_087_string_escape_quote():
#     source = '"He said \\"Hello\\""'
#     expected = 'He said \\"Hello\\",EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_088_string_escape_backslash():
#     source = '"path\\\\file"'
#     expected = 'path\\\\file,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_089_string_escape_backspace():
#     source = '"back\\bspace"'
#     expected = 'back\\bspace,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_090_string_escape_formfeed():
#     source = '"form\\ffeed"'
#     expected = 'form\\ffeed,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_091_string_escape_carriage_return():
#     source = '"carriage\\rreturn"'
#     expected = 'carriage\\rreturn,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_092_string_all_escapes():
#     source = '"\\b\\f\\r\\n\\t\\"\\\\"'
#     expected = '\\b\\f\\r\\n\\t\\"\\\\,EOF'  
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_093_string_multiple():
#     source = '"first" "second"'
#     expected = 'first,second,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # WHITESPACE TESTS
# # ============================================================================

# def test_094_whitespace_spaces():
#     """Multiple spaces should be ignored"""
#     source = "   int   x   "
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_095_whitespace_tabs():
#     source = "\tint\tx\t"
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_096_whitespace_newlines():
#     source = "int\nx\n"
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_097_whitespace_mixed():
#     source = "  \t\n\r\n  int \t x \n "
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_098_whitespace_formfeed():
#     source = "int\fx"
#     expected = "int,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # COMPLEX EXPRESSION TESTS
# # ============================================================================

# def test_099_expression_simple():
#     source = "x + y"
#     expected = "x,+,y,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_100_expression_complex():
#     source = "a * b + c / d - e % f"
#     expected = "a,*,b,+,c,/,d,-,e,%,f,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_101_expression_with_parentheses():
#     source = "(a + b) * (c - d)"
#     expected = "(,a,+,b,),*,(,c,-,d,),EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_102_expression_comparison():
#     source = "x >= y && z <= w"
#     expected = "x,>=,y,&&,z,<=,w,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_103_expression_assignment():
#     source = "x = y = z"
#     expected = "x,=,y,=,z,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_104_expression_increment_decrement():
#     source = "++x + y--"
#     expected = "++,x,+,y,--,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_105_expression_member_access():
#     source = "point.x = 10"
#     expected = "point,.,x,=,10,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_106_expression_negation():
#     source = "!flag"
#     expected = "!,flag,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # FUNCTION AND VARIABLE DECLARATION TESTS
# # ============================================================================

# def test_107_variable_declaration():
#     source = "int x;"
#     expected = "int,x,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_108_variable_declaration_with_init():
#     source = "auto x = 10;"
#     expected = "auto,x,=,10,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_109_function_declaration():
#     source = "void main() {}"
#     expected = "void,main,(,),{,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_110_function_with_params():
#     source = "int add(int x, int y)"
#     expected = "int,add,(,int,x,,,int,y,),EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_111_struct_declaration():
#     source = "struct Point { int x; int y; };"
#     expected = "struct,Point,{,int,x,;,int,y,;,},;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # CONTROL FLOW STATEMENT TESTS
# # ============================================================================

# def test_112_if_statement():
#     source = "if (x > 0) { return x; }"
#     expected = "if,(,x,>,0,),{,return,x,;,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_113_if_else_statement():
#     source = "if (x) { } else { }"
#     expected = "if,(,x,),{,},else,{,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_114_while_loop():
#     source = "while (i < 10) { ++i; }"
#     expected = "while,(,i,<,10,),{,++,i,;,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_115_for_loop():
#     source = "for (auto i = 0; i < 10; ++i) { }"
#     expected = "for,(,auto,i,=,0,;,i,<,10,;,++,i,),{,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_116_switch_statement():
#     source = "switch (x) { case 1: break; default: }"
#     expected = "switch,(,x,),{,case,1,:,break,;,default,:,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_117_break_statement():
#     source = "break;"
#     expected = "break,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_118_continue_statement():
#     source = "continue;"
#     expected = "continue,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_119_return_statement():
#     source = "return 42;"
#     expected = "return,42,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_120_return_void():
#     source = "return;"
#     expected = "return,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # EDGE CASES AND SPECIAL SCENARIOS
# # ============================================================================

# def test_121_adjacent_operators():
#     """Operators without spaces"""
#     source = "x==y"
#     expected = "x,==,y,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_122_double_plus_vs_increment():
#     """Test ++ vs + +"""
#     source = "x++ + ++y"
#     expected = "x,++,+,++,y,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_123_less_than_vs_left_shift():
#     """Test < vs <<"""
#     source = "x < y"
#     expected = "x,<,y,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_124_float_vs_dot_operator():
#     """Test 1.5 vs 1 . 5"""
#     source = "1.5"
#     expected = "1.5,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_125_identifier_starting_with_keyword():
#     """Identifiers that start with keywords"""
#     source = "integer floating automatic"
#     expected = "integer,floating,automatic,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_126_case_sensitivity():
#     """Test case sensitivity"""
#     source = "Int INT int"
#     expected = "Int,INT,int,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_127_mixed_case_keywords():
#     """Keywords must be exact case"""
#     source = "Void VOID void"
#     expected = "Void,VOID,void,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_128_numbers_and_identifiers():
#     """Numbers cannot start identifiers"""
#     source = "x123 123x"
#     expected = "x123,123,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_129_underscore_variations():
#     """Various underscore uses"""
#     source = "_ __ _x x_ _x_"
#     expected = "_,__,_x,x_,_x_,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # COMPREHENSIVE PROGRAM TESTS
# # ============================================================================

# def test_130_simple_program():
#     """Complete simple program"""
#     source = """void main() {
#         auto x = 10;
#         printInt(x);
#     }"""
#     expected = "void,main,(,),{,auto,x,=,10,;,printInt,(,x,),;,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_131_function_with_return():
#     """Function with parameters and return"""
#     source = """int add(int x, int y) {
#         return x + y;
#     }"""
#     expected = "int,add,(,int,x,,,int,y,),{,return,x,+,y,;,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_132_struct_example():
#     """Struct declaration and usage"""
#     source = """struct Point { int x; int y; };
#     Point p = {10, 20};"""
#     expected = "struct,Point,{,int,x,;,int,y,;,},;,Point,p,=,{,10,,,20,},;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_133_complex_expression_statement():
#     """Complex mathematical expression"""
#     source = "result = (a + b) * c - d / e % f;"
#     expected = "result,=,(,a,+,b,),*,c,-,d,/,e,%,f,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_134_nested_control_flow():
#     """Nested if and while"""
#     source = """if (x > 0) {
#         while (y < 10) {
#             ++y;
#         }
#     }"""
#     expected = "if,(,x,>,0,),{,while,(,y,<,10,),{,++,y,;,},},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # LITERAL EDGE CASES
# # ============================================================================

# def test_135_very_large_integer():
#     """Very large integer literal"""
#     source = "9999999999"
#     expected = "9999999999,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_136_very_small_float():
#     source = "0.00001"
#     expected = "0.00001,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_137_float_exponent_variations():
#     """Different exponent formats"""
#     source = "1e10 1E10 1e+10 1E-10"
#     expected = "1e10,1E10,1e+10,1E-10,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_138_float_decimal_variations():
#     """Different decimal formats"""
#     source = ".123 123. 1.23"
#     expected = ".123,123.,1.23,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_139_zero_variations():
#     """Different zero representations"""
#     source = "0 0.0 0. .0 0e0"
#     expected = "0,0.0,0.,.0,0e0,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # OPERATOR COMBINATION TESTS
# # ============================================================================

# def test_140_all_relational_operators():
#     """All comparison operators"""
#     source = "a < b <= c > d >= e == f != g"
#     expected = "a,<,b,<=,c,>,d,>=,e,==,f,!=,g,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_141_all_arithmetic_operators():
#     """All arithmetic operators"""
#     source = "a + b - c * d / e % f"
#     expected = "a,+,b,-,c,*,d,/,e,%,f,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_142_unary_operators():
#     """Unary operators"""
#     source = "+x -y !z ++a --b"
#     expected = "+,x,-,y,!,z,++,a,--,b,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_143_postfix_operators():
#     """Postfix increment and decrement"""
#     source = "x++ y--"
#     expected = "x,++,y,--,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_144_mixed_increment():
#     """Pre and post increment"""
#     source = "++x++ + x++ ++x"
#     expected = "++,x,++,+,x,++,++,x,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # STRING SPECIAL CASES
# # ============================================================================

# def test_145_string_with_numbers():
#     source = '"12345"'
#     expected = '12345,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_146_string_with_special_chars():
#     source = '"!@#$%^&*()"'
#     expected = '!@#$%^&*(),EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_147_string_consecutive():
#     source = '""""""'
#     expected = ',,,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_148_string_with_keywords():
#     source = '"int float void"'
#     expected = 'int float void,EOF'
#     assert Tokenizer(source).get_tokens_as_string() == expected


# # ============================================================================
# # MULTILINE TESTS
# # ============================================================================

# def test_149_multiline_statement():
#     """Statement spanning multiple lines"""
#     source = """x = 
#     y + 
#     z;"""
#     expected = "x,=,y,+,z,;,EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected


# def test_150_multiline_function():
#     """Function declaration spanning multiple lines"""
#     source = """int
#     add
#     (
#     int x,
#     int y
#     )
#     {
#     return x + y;
#     }"""
#     expected = "int,add,(,int,x,,,int,y,),{,return,x,+,y,;,},EOF"
#     assert Tokenizer(source).get_tokens_as_string() == expected

def test_001():
    source = """\t\r\n
    /* This is a block comment so // has no meaning here */
    // VOTIEN
"""
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_002():
    source = "@"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token @"

def test_003():
    source = "auto auto1"
    expected = "auto,auto1,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_004():
    source = "+ ++"
    expected = "+,++,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_005():
    source = "votien123"
    expected = "votien123,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_006():
    source = "0   100   255   2500   -45"
    expected = "0,100,255,2500,-,45,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_007():
    source = "0.0   3.14   -2.5   1.23e4   5.67E-2   1.   .5"
    expected = "0.0,3.14,-,2.5,1.23e4,5.67E-2,1.,.5,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_008():
    source = """
    "This is a string containing tab \\t"
    "He asked me: \\"Where is John?\\""
"""
    expected = "This is a string containing tab \\t,He asked me: \\\"Where is John?\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_009():
    source = """
    "This is a string \n containing tab \\t"
"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: This is a string "
    
def test_010():
    source = """
    "This is a string \\z containing tab \\t"
"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Illegal Escape In String: This is a string \\z"

def test_011():
    source = """
    auto break case continue default else float for if int
    return string struct switch void while
    """
    expected = (
        "auto,break,case,continue,default,else,float,for,if,int,"
        "return,string,struct,switch,void,while,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_012():
    source = """
    + - * / % == != < > <= >= || && ! ++ -- = .
    """
    expected = (
        "+,-,*,/,%,==,!=,<,>,<=,>=,||,&&,!,++,--,=,.,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_013():
    source = """
    { } ( ) ; , :
    """
    expected = "{,},(,),;,,,:,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_014():
    source = """
    a A _ _a a1 a_1 A123 _ABC abc_DEF123
    """
    expected = (
        "a,A,_,_a,a1,a_1,A123,_ABC,abc_DEF123,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_015():
    source = """
   ++ +- -+ + + - - +++
    """
    expected = (
        "++,+,-,-,+,+,+,-,-,++,+,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_016():
    source = "^"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token ^"

def test_017():
    source = "&"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token &"

def test_018():
    source = "\\"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token \\"

def test_019():
    source = "autoauto"
    expected = (
        "autoauto,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_020():
    source = "12ab34 a-b"
    expected = (
        "12,ab34,a,-,b,EOF"
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_021():
    source = "~"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token ~"

def test_022():
    source = "0 5 123 -0 -45 99999"
    expected = "0,5,123,-,0,-,45,99999,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_023():
    source = "000 -000 0123 -00502"
    expected = "000,-,000,0123,-,00502,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_024():
    source = "+000 +123 +-025"
    expected = "+,000,+,123,+,-,025,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_025():
    source = "12_3"
    expected = "12,_3,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_026():
    source = "0x123"
    expected = "0,x123,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_027():
    """skip"""
    source = "\t \n \r \n \t   "
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_028():
    """skip"""
    source = "\f  "
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_029():
    """skip"""
    source = "\t \n \r \n \t   "
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_030():
    source = "//include <iostream>"
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_031():
    source = "// this is a comment\nint x"
    expected = "int,x,EOF" 
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_032():
    source = "/* multi line \n comment */ float y"
    expected = "float,y,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_033():
    source = "int a // comment here\nfloat b"
    expected = "int,a,float,b,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_034():
    source = "/* outer /* inner */ still comment */ boolean c"
    expected = "still,comment,*,/,boolean,c,EOF" 
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_035():
    source = "   \t\r\n\f // just comment\n   /* another */   "
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_036():
    source = "// Python comment\nint x"
    expected = "int,x,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_037():
    source = "// C++ style comment\nfloat y"
    expected = "float,y,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_038():
    source = "/* multi-line comment */ boolean z"
    expected = "boolean,z,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_039():
    source = "// Rust or Go comment\nstring s"
    expected = "string,s,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_040():
    source = "<!-- HTML style comment --> int a"
    expected = "<,!,--,HTML,style,comment,--,>,int,a,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_041():
    source = "## python"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token #"

def test_042():
    source = "# python"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token #"

def test_043():
    source = "int &a := 10;"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token &"

def test_044():
    source = ">> **"
    expected = ">,>,*,*,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_045():
    source = '"Hello\\nWorld! \\"test\\" \\\\"'
    expected = 'Hello\\nWorld! \\"test\\" \\\\,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_046():
    """Test Unclosed string with newline"""
    source = '"Unclosed string line\nlet x = 5;'
    expected = 'Unclosed String: Unclosed string line'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_047():
    source = '"Missing end quote'
    expected = 'Unclosed String: Missing end quote'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_048():
    source = '"Escape with \\x invalid"'
    expected = 'Illegal Escape In String: Escape with \\x'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_049():
    source = '"abc\\\\ \\ "'
    expected = 'Illegal Escape In String: abc\\\\ \\ '
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_050():
    source = (
        '"abc" '
        '"\\n" '
        '"\\t" '
        '"\\r" '
        '"\\\"" '
        '"\\\\" '
        '"" '
        '"Hello\\nWorld\\tTabbed\\rCarriage\\"Quote\\\\"'
    )
    expected = (
        'abc,\\n,\\t,\\r,\\",\\\\,,'
        'Hello\\nWorld\\tTabbed\\rCarriage\\"Quote\\\\,EOF'
    )
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_051():
    source = '"This is a string\r\nlet x = 1;'
    expected = 'Unclosed String: This is a string'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_052():
    source = '"Another line\nlet x = 2;'
    expected = 'Unclosed String: Another line'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_053():
    source = '"End with EOF'
    expected = 'Unclosed String: End with EOF'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_054():
    source = '"Escape with \\f valid"'
    expected = 'Escape with \\f valid,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_055():
    source = '"Escape with \\b valid"'
    expected = 'Escape with \\b valid,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_056():
    source = '"Escape with \'" invalid"'
    expected = 'Unclosed String: '
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_057():
    source = '"Escape with \\z"'
    expected = 'Illegal Escape In String: Escape with \\z'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_058():
    source = '"Escape with \\*"'
    expected = 'Illegal Escape In String: Escape with \\*'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_059():
    source = "let x := 0; /* outer /* inner */ still outer */ x := 1;"
    expected = "let,x,:,=,0,;,still,outer,*,/,x,:,=,1,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_060():
    """Valid simple string"""
    source = '"Hello World"'
    expected = "Hello World,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_061():
    """Valid string with escape sequences"""
    source = '"Line1\\nLine2\\tTabbed\\rCarriage\\\\"'
    expected = "Line1\\nLine2\\tTabbed\\rCarriage\\\\,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_062():
    source = '"He said: \\"Hello\\" "'
    expected = 'He said: \\"Hello\\" ,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_063():
    source = '""'
    expected = ",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_064():
    source = '"Unclosed string\nlet x = 1;'
    expected = 'Unclosed String: Unclosed string'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_065():
    source = '"Another unclosed string'
    expected = 'Unclosed String: Another unclosed string'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_066():
    source = '"Escape with \\x invalid"'
    expected = 'Illegal Escape In String: Escape with \\x'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected but no exception was raised"
    except Exception as e:
        assert str(e) == expected

def test_067():
    source = '"This is invalid: \'"'
    expected = 'This is invalid: \',EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_068():
    source = '"Ends with backslash\\\\"'
    expected = 'Ends with backslash\\\\,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_069():
    source = '"\\b\\f\\r\\n\\t\\\""'
    expected = '\\b\\f\\r\\n\\t\\",EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_070():
    source = '"Hello\\nWorld! \\"Quote\\" and \\\\Backslash"'
    expected = 'Hello\\nWorld! \\"Quote\\" and \\\\Backslash,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_071():
    source = '0. 0.9 0e2 0.e-2 '
    expected = '0.,0.9,0e2,0.e-2,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_072():
    source = '123.45E-6'
    expected = '123.45E-6,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_073():
    source = '123.456'
    expected = '123.456,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_074():
    source = '123e10'
    expected = '123e10,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_075():
    source = '0.33E+3'
    expected = '0.33E+3,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_076():
    source = "1. 0.5 123.456 42e3 7E+2 9e-10 3.14e10 6.022E23 0.1E-3 10.0e+5"
    expected = "1.,0.5,123.456,42e3,7E+2,9e-10,3.14e10,6.022E23,0.1E-3,10.0e+5,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_077():
    """Test invalid float: missing integer part before dot"""
    source = '.5 -.055'
    expected = '.5,-,.055,EOF' 
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_078():
    """Test invalid float: incomplete exponent part"""
    source = '1e'
    expected = '1,e,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_079():
    source = 'e10'
    expected = 'e10,EOF'
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_080():
    source = '4.5.6 12a.3'
    expected = '4.5,.6,12,a,.3,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_081():
    source = '001e+02 -1. -2.0e-02'
    expected = '001e+02,-,1.,-,2.0e-02,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_082():
    source = '.e-2'
    expected = '.,e,-,2,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_083():
    source = '0.0 3.14 1.23e4 5.67E-2 1. .5 1e4 2E-3'
    expected = '0.0,3.14,1.23e4,5.67E-2,1.,.5,1e4,2E-3,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_084():
    source = '.010e-0.5'
    expected = '.010e-0,.5,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_085():
    source = '-12e-5'
    expected = '-,12e-5,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_086():
    source = "["
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token ["

def test_087():
    source = "]"
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token ]"

def test_088():
    source = '"Extended ASCII: \x80\xFF" '
    expected = 'Extended ASCII: \x80\xFF,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_089():
    source = '-12.1e-2'
    expected = '-,12.1e-2,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_090():
    source = '"a\r\n"'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: a"

def test_091():
    source = '"a\\r\\n"'
    expected = 'a\\r\\n,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_092():
    source =  """ "a\\\n """
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: a\\"

def test_093():
    source = '"a'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: a"

def test_094():
    source = '"a'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: a"

def test_095():
    source = " \"ab\\'ab \"   "
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Illegal Escape In String: ab\\'"


def test_096():
    source = '123.e'
    expected = '123.,e,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_097():
    source = '-.a'
    expected = '-,.,a,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_098():
    source = '-10 -1.0'
    expected = '-,10,-,1.0,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_099():
    source = '"abc\n\n"'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: abc"


def test_099():
    source = '-.'
    expected = '-,.,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_100():
    source = '@ab'
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Error Token @"

def test_101():
    source = '.e12'
    expected = '.,e12,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_102():
    source = '.e12'
    expected = '.,e12,EOF'  
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_103():
    source =  """ "a\\
"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: a\\"

def test_104():
    source =  """ "'a\\"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: 'a\\"

def test_105():
    source =  """\""""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: "

def test_106():
    source =  """\"\n"""
    try:
        Tokenizer(source).get_tokens_as_string()
        assert False, "Expected ErrorToken but no exception was raised"
    except Exception as e:
        assert str(e) == "Unclosed String: "
