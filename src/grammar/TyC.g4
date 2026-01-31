grammar TyC;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:       
        result = super().emit();
        raise UncloseString(result.text[1:]);
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit();
        raise IllegalEscape(result.text[1:]);
    elif tk == self.ERROR_CHAR:
        result = super().emit();
        raise ErrorToken(result.text); 
    else:
        return super().emit();
}

options{
	language=Python3;
}

// TODO: Define grammar rules here


//====================================PARSER===========================================

//---------------PROGRAM STRUCTURE------------------
program: 
    (struct_decl | func_decl)* EOF
    ;

//---------------STRUCT DECLARATION-----------------
struct_decl:
    STRUCT ID LBRACE struct_mem* RBRACE SEMI
    ;

struct_mem:
    type ID SEMI
    ;

//---------------FUNCTION DECLARATION---------------
func_decl:
    return_type? ID LPAREN param_list? RPAREN block_stmt
    ;

return_type:
    type | VOID_KW
    ;

param_list:
    param (COMMA param)*
    ;

param:
    type ID
    ;

type:
    INT_KW | FLOAT_KW | STRING_KW | ID
    ;


//---------------STATEMENT--------------------------
stmt:
    var_dec_stmt | block_stmt | assign_stmt | if_stmt | while_stmt
    | for_stmt | switch_stmt | break_stmt | continue_stmt | return_stmt | expr_stmt
    ;

var_dec_stmt:
    AUTO ID (ASSIGN expr)? SEMI
    | type ID (ASSIGN initializer)? SEMI
    ;

initializer:
    expr | LBRACE initializer_list RBRACE
    ;

initializer_list:
    initializer (COMMA initializer)*
    ;

block_stmt:
    LBRACE (stmt)* RBRACE
    ;

assign_stmt:
    left_value ASSIGN expr SEMI
    ;

left_value:
    ID (MEM_ACCESS ID)*
    ;


if_stmt:
    IF LPAREN expr RPAREN stmt (ELSE stmt)?
    ;

while_stmt:
    WHILE LPAREN expr RPAREN stmt
    ;

for_stmt:
    FOR LPAREN init SEMI expr? SEMI expr? RPAREN stmt
    ;

init:
    AUTO ID (ASSIGN expr)? |  type ID (ASSIGN expr)? | left_value ASSIGN expr
    ;


switch_stmt:
    SWITCH LPAREN expr RPAREN LBRACE switch_section* RBRACE
    ;

switch_section:
    case_block | default_block
    ;

case_block:
    CASE case_expr COLON stmt*
    ;

case_expr:
    (ADD | SUB)? INT | LPAREN expr RPAREN 
    ;

default_block:
    DEFAULT COLON stmt*
    ;

continue_stmt:
    CONTINUE SEMI
    ;

return_stmt:
    RETURN expr? SEMI
    ;

expr_stmt:
    expr SEMI
    ;

break_stmt:
    BREAK SEMI
    ;

//---------------------EXPRESSION------------------------
expr:
    assignment_expr
    ;

assignment_expr:
    logical_OR_expr | left_value ASSIGN assignment_expr
    ;

logical_OR_expr:
    logical_OR_expr OR logical_AND_expr | logical_AND_expr
    ;

logical_AND_expr:
    logical_AND_expr AND equality_expr | equality_expr
    ;

equality_expr:
    equality_expr (EQ | NEQ) relational_expr | relational_expr
    ;

relational_expr:
    relational_expr (LT | GT | LEQ | GEQ) additive_expr | additive_expr
    ;

additive_expr:
    additive_expr (ADD | SUB) multiplicative_expr | multiplicative_expr
    ;

multiplicative_expr:
    multiplicative_expr (MUL | DIV | MOD) unary_expr | unary_expr
    ;

unary_expr:
    (ADD | SUB | NOT) unary_expr
    | prefix_expr
    ;

prefix_expr:
    (INC | DEC) prefix_expr | postfix_expr
    ;

//postfix_expr:
//    postfix_expr (INC | DEC ) | mem_access_expr
//    ;

postfix_expr:
    primary_expr postfix_tail
    ;

postfix_tail:
    (MEM_ACCESS ID | INC | DEC) postfix_tail
    | /* epsilon */
    ;

//mem_access_expr:
//    mem_access_expr (MEM_ACCESS ID) | primary_expr
//    ;

primary_expr:
    ID | literal | LPAREN expr RPAREN | function_call
    ;

literal:
    INT | FLOAT | STRING
    ;

function_call:
    ID LPAREN arg_list? RPAREN
    ;

arg_list:
    expr (COMMA expr)*
    ;
//==========================================================================================

//=========================================LEXER============================================
fragment LETTER:
    [A-Za-z]
    ;

fragment DIGIT:
    [0-9]
    ;

fragment ESC_SEQ:
    '\\' [btnfr"\\]
    ;

ILLEGAL_ESCAPE:
    '"' (~["\\\r\n] | ESC_SEQ)* '\\' ~[btnfr"\\\r\n]
    ;

UNCLOSE_STRING:
    '"' (ESC_SEQ | ~["\\\r\n])* (EOF | '\r' | '\n')
    ;

//-----------------KEYWORD-------------------
AUTO: 'auto';
BREAK: 'break';
CASE: 'case';
CONTINUE: 'continue';
DEFAULT: 'default';
ELSE: 'else';
FLOAT_KW: 'float';
FOR: 'for';
IF: 'if';
INT_KW: 'int';
RETURN: 'return';
STRING_KW: 'string';
STRUCT: 'struct';
SWITCH: 'switch';
VOID_KW: 'void';
WHILE: 'while';

//-----------------OPERATOR-------------------
INC: '++';
DEC: '--';
ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
MOD: '%';
EQ: '==';
NEQ: '!=';
LEQ: '<=';
GEQ: '>=';
LT: '<';
GT: '>';
OR: '||';
AND: '&&';
NOT: '!';
ASSIGN: '=';
MEM_ACCESS: '.';

//----------------SEPARATOR------------------
LBRACE: '{';
RBRACE: '}';
LPAREN: '(';
RPAREN: ')';
SEMI: ';';
COMMA: ',';
COLON: ':';

INT: 
    DIGIT+
    ;

fragment EXP: [eE] [+-]? DIGIT+;

FLOAT:
    (DIGIT+ '.' DIGIT* EXP?) | DIGIT+ EXP | '.' DIGIT+ EXP?
    ;

STRING:
    '"' (ESC_SEQ | ~["\\\r\n])* '"'
    {
        self.text = self.text[1:-1]
    }
    ;


//----------------IDENTIFIER-----------------
ID: 
    (LETTER | '_')(LETTER | DIGIT | '_')*
    ;

WS : [ \t\r\n]+ -> skip ; // skip spaces, tabs

LINE_COMMENT: 
    '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

ERROR_CHAR: .;
//===========================================================================