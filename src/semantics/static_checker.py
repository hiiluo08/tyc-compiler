"""
Static Semantic Checker for TyC Programming Language

This module implements a comprehensive static semantic checker using visitor pattern
for the TyC procedural programming language. It performs type checking,
scope management, type inference, and detects all semantic errors as
specified in the TyC language specification.
"""

from functools import reduce
from typing import (
    Dict,
    List,
    Set,
    Optional,
    Any,
    Tuple,
    NamedTuple,
    Union,
    TYPE_CHECKING,
)
from ..utils.visitor import ASTVisitor
from ..utils.nodes import (
    ASTNode,
    Program,
    StructDecl,
    MemberDecl,
    FuncDecl,
    Param,
    VarDecl,
    IfStmt,
    WhileStmt,
    ForStmt,
    BreakStmt,
    ContinueStmt,
    ReturnStmt,
    BlockStmt,
    SwitchStmt,
    CaseStmt,
    DefaultStmt,
    Type,
    IntType,
    FloatType,
    StringType,
    VoidType,
    StructType,
    BinaryOp,
    PrefixOp,
    PostfixOp,
    AssignExpr,
    MemberAccess,
    FuncCall,
    Identifier,
    StructLiteral,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    ExprStmt,
    Expr,
    Stmt,
    Decl,
)

# Type aliases for better type hints
TyCType = Union[IntType, FloatType, StringType, VoidType, StructType]
from .static_error import (
    StaticError,
    Redeclared,
    UndeclaredIdentifier,
    UndeclaredFunction,
    UndeclaredStruct,
    TypeCannotBeInferred,
    TypeMismatchInStatement,
    TypeMismatchInExpression,
    MustInLoop,
)

class AutoType(Type):
    def __init__(self):
        super().__init__()

    def accept(self, visitor, o=None):
        return visitor.visit_auto_type(self, o)

    def __str__(self):
        return "AutoType()"

class CheckerContext:
    def __init__(self):
        self.local_env = [{}]
        self.global_funcs = {}
        self.global_structs = {}
        self.in_loop = 0
        self.in_switch = 0
        self.current_func_return_type = None
        self.current_func_name = None
    
    def push_scope(self):
        self.local_env.append({})
    
    def pop_scope(self):
        self.local_env.pop()
    
    def initialize_builtins(self):
        self.global_funcs['readInt'] = ([], IntType())
        self.global_funcs['readFloat'] = ([], FloatType())
        self.global_funcs['readString'] = ([], StringType())
        self.global_funcs['printInt'] = ([IntType()], VoidType())
        self.global_funcs['printFloat'] = ([FloatType()], VoidType())
        self.global_funcs['printString'] = ([StringType()], VoidType())

    
def update_inferred_type(rhs, inferred_type, o: CheckerContext):
    if isinstance(rhs, Identifier):
        for env in reversed(o.local_env):
            if rhs.name in env:
                env[rhs.name] = inferred_type
                return
        
    elif isinstance(rhs, FuncCall):
        if rhs.name in o.global_funcs:
            param_types, _ = o.global_funcs[rhs.name]
            o.global_funcs[rhs.name] = (param_types, inferred_type)


class StaticChecker(ASTVisitor):
    def check_program(self, ast):
        ctx = CheckerContext()
        ctx.initialize_builtins()
        return self.visit(ast, ctx)

    def visit_program(self, node: "Program", o: CheckerContext):
        for decl in node.decls:
            if isinstance(decl, StructDecl):
                if decl.name in o.global_structs:
                    raise Redeclared('Struct', decl.name)
                o.global_structs[decl.name] = {}
                self.visit(decl, o)

            elif isinstance(decl, FuncDecl):
                if decl.name in o.global_funcs:
                    raise Redeclared('Function', decl.name)

                param_types = [self.visit(param.param_type, o) for param in decl.params]

                return_type = self.visit(decl.return_type, o) if decl.return_type else AutoType()

                o.global_funcs[decl.name] = (param_types, return_type)
                self.visit(decl, o)


    def visit_struct_decl(self, node: "StructDecl", o: CheckerContext):
        for member in node.members:
            if member.name in o.global_structs[node.name]:
                raise Redeclared('Member', member.name)

            member_type = self.visit(member.member_type, o)

            o.global_structs[node.name][member.name] = member_type


    def visit_member_decl(self, node: "MemberDecl", o: CheckerContext):
        pass


    def visit_func_decl(self, node: "FuncDecl", o: CheckerContext):
        param_types, return_type = o.global_funcs[node.name]

        param_names = []
        for param in node.params:
            if param.name in param_names:
                raise Redeclared('Parameter', param.name)
            param_names.append(param.name)

        o.push_scope()
        o.current_func_name = node.name
        o.current_func_return_type = return_type
        for param in node.params:
            o.local_env[-1][param.name] = param.param_type

        for stmt in node.body.statements:
            self.visit(stmt, o)
        
        o.pop_scope()
    

    def visit_param(self, node: "Param", o: CheckerContext):
        pass

    # Type system
    def visit_int_type(self, node: "IntType", o: CheckerContext):
        return node

    def visit_float_type(self, node: "FloatType", o: CheckerContext):
        return node

    def visit_string_type(self, node: "StringType", o: CheckerContext):
        return node

    def visit_void_type(self, node: "VoidType", o: CheckerContext):
        return node

    def visit_struct_type(self, node: "StructType", o: CheckerContext):
        if node.struct_name not in o.global_structs:
            raise UndeclaredStruct(node.struct_name)
        return node

    # Statements
    def visit_block_stmt(self, node: "BlockStmt", o: CheckerContext):
        o.push_scope()

        for stmt in node.statements:
            self.visit(stmt, o)
        
        o.pop_scope()

    def visit_var_decl(self, node: "VarDecl", o: CheckerContext):
        if node.name in o.local_env[-1]:
            raise Redeclared('Variable', node.name)
        
        lhs_type = self.visit(node.var_type, o) if node.var_type else AutoType()

        if node.init_value:
            rhs_type = self.visit(node.init_value, o)

            if isinstance(lhs_type, AutoType):
                if isinstance(rhs_type, AutoType):
                    raise TypeCannotBeInferred(node)
                if isinstance(rhs_type, StructLiteral):
                    raise TypeCannotBeInferred(node)
                lhs_type = rhs_type
            elif isinstance(lhs_type, StructType):
                if not isinstance(rhs_type, StructLiteral):
                    raise TypeMismatchInStatement(node)
                
                struct_fields = o.global_structs[lhs_type.struct_name]
                if len(rhs_type.values) != len(struct_fields):
                    raise TypeMismatchInStatement(node)
                
                for val, field_type in zip(rhs_type.values, struct_fields.values()):
                    val_type = self.visit(val, o)
                    if isinstance(val_type, StructLiteral):
                        pass
                    elif type(val_type) != type(field_type):
                        raise TypeMismatchInStatement(node)
                    elif isinstance(field_type, StructType) and val_type.struct_name != field_type.struct_name:
                        raise TypeMismatchInStatement(node)
            else:
                if isinstance(rhs_type, AutoType):
                    update_inferred_type(node.init_value, lhs_type, o)
                else:
                    if type(lhs_type) != type(rhs_type):
                        raise TypeMismatchInStatement(node)
                    
                    if isinstance(lhs_type, StructType) and isinstance(rhs_type, StructType):
                        if lhs_type.struct_name != rhs_type.struct_name:
                            raise TypeMismatchInStatement(node)
        
        o.local_env[-1][node.name] = lhs_type 


    def visit_if_stmt(self, node: "IfStmt", o: CheckerContext):
        condition_type = self.visit(node.condition, o)
        if not isinstance(condition_type, IntType):
            raise TypeMismatchInStatement(node)

        self.visit(node.then_stmt, o)
        
        if node.else_stmt:
            self.visit(node.else_stmt, o)

    def visit_while_stmt(self, node: "WhileStmt", o: CheckerContext):
        o.in_loop += 1

        condition_type = self.visit(node.condition, o)
        if not isinstance(condition_type, IntType):
            raise TypeMismatchInStatement(node)
        
        self.visit(node.body, o)
        
        o.in_loop -= 1

    def visit_for_stmt(self, node: "ForStmt", o: CheckerContext):
        o.in_loop += 1
        o.push_scope()

        if node.init:
            self.visit(node.init, o)
        
        if node.condition:
            condition_type = self.visit(node.condition, o)
            if not isinstance(condition_type, IntType):
                raise TypeMismatchInStatement(node)
        
        if node.update:
            self.visit(node.update, o)
        
        self.visit(node.body, o)

        o.pop_scope()
        o.in_loop -= 1
        

    def visit_switch_stmt(self, node: "SwitchStmt", o: CheckerContext):
        o.in_switch += 1

        expr_type = self.visit(node.expr, o)
        if not isinstance(expr_type, IntType):
            raise TypeMismatchInStatement(node)

        for case in node.cases:
            self.visit(case, o)
        
        if node.default_case:
            self.visit(node.default_case, o)

        o.in_switch -= 1

    def visit_case_stmt(self, node: "CaseStmt", o: CheckerContext):
        case_type = self.visit(node.expr, o)
        if not isinstance(case_type, IntType):
            raise TypeMismatchInStatement(node)

        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_default_stmt(self, node: "DefaultStmt", o: CheckerContext):
        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_break_stmt(self, node: "BreakStmt", o: CheckerContext):
        if o.in_loop or o.in_switch:
            return
        raise MustInLoop(node)

    def visit_continue_stmt(self, node: "ContinueStmt", o: CheckerContext):
        if o.in_loop:
            return
        raise MustInLoop(node)

    def visit_return_stmt(self, node: "ReturnStmt", o: CheckerContext):
        if isinstance(o.current_func_return_type, VoidType):
            if node.expr:
                raise TypeMismatchInStatement(node)
            return
        if not node.expr:
            raise TypeMismatchInStatement(node)
        
        return_type = self.visit(node.expr, o)
        
        if isinstance(o.current_func_return_type, AutoType):
            if isinstance(return_type, AutoType):
                raise TypeCannotBeInferred(node)
            o.current_func_return_type = return_type
            param_types, _ = o.global_funcs[o.current_func_name]
            o.global_funcs[o.current_func_name] = (param_types, return_type)
        else:
            if isinstance(return_type, AutoType):
                raise TypeMismatchInStatement(node)
            if isinstance(o.current_func_return_type, StructType) and isinstance(return_type, StructLiteral):
                struct_fields = o.global_structs[o.current_func_return_type.struct_name]
                if len(return_type.values) != len(struct_fields):
                    raise TypeMismatchInStatement(node)
                for val, field_type in zip(return_type.values, struct_fields.values()):
                    val_type = self.visit(val, o)
                    if isinstance(val_type, StructLiteral):
                        pass
                    elif type(val_type) != type(field_type):
                        raise TypeMismatchInStatement(node)
                    elif isinstance(field_type, StructType) and val_type.struct_name != field_type.struct_name:
                        raise TypeMismatchInStatement(node)
                return
            if isinstance(o.current_func_return_type, StructType) and isinstance(return_type, StructType):
                if return_type.struct_name != o.current_func_return_type.struct_name:
                    raise TypeMismatchInStatement(node)
                return
            if type(return_type) != type(o.current_func_return_type):
                raise TypeMismatchInStatement(node)

    def visit_expr_stmt(self, node: "ExprStmt", o: CheckerContext):
        self.visit(node.expr, o)

    # Expressions
    def visit_binary_op(self, node: "BinaryOp", o: CheckerContext):
        lhs_type = self.visit(node.left, o)
        rhs_type = self.visit(node.right, o)

        arithmetic_op = ['+', '-', '*', '/']
        relational_op = ['==', '!=', '<', '<=', '>', '>=']
        logical_op = ['&&', '||']
        num_type = (IntType, FloatType)

        if isinstance(lhs_type, AutoType) or isinstance(rhs_type, AutoType):
            if node.operator in arithmetic_op or node.operator in relational_op:
                raise TypeCannotBeInferred(node)
            elif node.operator in logical_op or node.operator == '%':
                if isinstance(lhs_type, AutoType):
                    update_inferred_type(node.left, IntType(), o)
                    lhs_type = IntType()
                if isinstance(rhs_type, AutoType):
                    update_inferred_type(node.right, IntType(), o)
                    rhs_type = IntType()

        if node.operator in arithmetic_op:
            if not isinstance(lhs_type, num_type) or not isinstance(rhs_type, num_type):
                raise TypeMismatchInExpression(node)
            return FloatType() if isinstance(lhs_type, FloatType) or isinstance(rhs_type, FloatType) else IntType()

        if node.operator == '%' or node.operator in logical_op:
            if not isinstance(lhs_type, IntType) or not isinstance(rhs_type, IntType):
                raise TypeMismatchInExpression(node)
            return IntType()
        
        if node.operator in relational_op:
            if not isinstance(lhs_type, num_type) or not isinstance(rhs_type, num_type):
                raise TypeMismatchInExpression(node)
            return IntType()


    def visit_prefix_op(self, node: "PrefixOp", o: CheckerContext):
        operand_type = self.visit(node.operand, o)

        if isinstance(operand_type, AutoType) and node.operator in ['+', '-']:
            raise TypeCannotBeInferred(node)
        
        if isinstance(operand_type, AutoType) and node.operator in ['!', '++', '--']:
            update_inferred_type(node.operand, IntType(), o)
            operand_type = IntType()

        num_type = (IntType, FloatType)
        if node.operator in ['+', '-']:
            if not isinstance(operand_type, num_type):
                raise TypeMismatchInExpression(node)
            return operand_type
        
        if node.operator in ['!', '++', '--']:
            if not isinstance(operand_type, IntType):
                raise TypeMismatchInExpression(node)
            if node.operator in ['++', '--']:
                if not isinstance(node.operand, Identifier) and not isinstance(node.operand, MemberAccess):
                    raise TypeMismatchInExpression(node)
            return IntType()

    def visit_postfix_op(self, node: "PostfixOp", o: CheckerContext):
        operand_type = self.visit(node.operand, o)

        if isinstance(operand_type, AutoType):
            update_inferred_type(node.operand, IntType(), o)
            operand_type = IntType()

        if not isinstance(operand_type, IntType):
            raise TypeMismatchInExpression(node)

        if not isinstance(node.operand, Identifier) and not isinstance(node.operand, MemberAccess):
            raise TypeMismatchInExpression(node)

        return IntType()

    def visit_assign_expr(self, node: "AssignExpr", o: CheckerContext):
        lhs_type = self.visit(node.lhs, o)
        rhs_type = self.visit(node.rhs, o)

        if isinstance(node.lhs, Identifier) or isinstance(node.lhs, MemberAccess):
            if isinstance(lhs_type, AutoType) and isinstance(rhs_type, AutoType):
                raise TypeCannotBeInferred(node)
            
            if isinstance(lhs_type, AutoType):
                update_inferred_type(node.lhs, rhs_type, o)
                lhs_type = rhs_type
            if isinstance(rhs_type, AutoType):
                update_inferred_type(node.rhs, lhs_type, o)
                rhs_type = lhs_type
            
            if type(lhs_type) is not type(rhs_type):
                raise TypeMismatchInExpression(node)
            
            if isinstance(lhs_type, StructType):
                if lhs_type.struct_name != rhs_type.struct_name:
                    raise TypeMismatchInExpression(node)
                
            return lhs_type
            
        raise TypeMismatchInExpression(node)

    def visit_assign_stmt(self, node, o: CheckerContext):
        assign_expr = node
        for k, v in vars(node).items():
            if k not in ['line', 'column'] and v is not None:
                assign_expr = v
                break

        lhs_type = self.visit(assign_expr.lhs, o)
        rhs_type = self.visit(assign_expr.rhs, o)

        if isinstance(assign_expr.lhs, Identifier) or isinstance(assign_expr.lhs, MemberAccess):
            if isinstance(lhs_type, AutoType) and isinstance(rhs_type, AutoType):
                raise TypeCannotBeInferred(node)
            
            if isinstance(lhs_type, AutoType):
                update_inferred_type(assign_expr.lhs, rhs_type, o)
                lhs_type = rhs_type
            if isinstance(rhs_type, AutoType):
                update_inferred_type(assign_expr.rhs, lhs_type, o)
                rhs_type = lhs_type
            
            if type(lhs_type) is not type(rhs_type):
                raise TypeMismatchInStatement(node)
            
            if isinstance(lhs_type, StructType):
                if lhs_type.struct_name != rhs_type.struct_name:
                    raise TypeMismatchInStatement(node)
                
            return
            
        raise TypeMismatchInStatement(node)

    def visit_member_access(self, node: "MemberAccess", o: CheckerContext):
        obj_type = self.visit(node.obj, o)

        if isinstance(obj_type, AutoType):
            raise TypeCannotBeInferred(node.obj)
        
        if not isinstance(obj_type, StructType):
            raise TypeMismatchInExpression(node)
        
        struct_fields = o.global_structs[obj_type.struct_name]
        if node.member not in struct_fields:
            raise UndeclaredIdentifier(node.member)
        
        return struct_fields[node.member]

    def visit_func_call(self, node: "FuncCall", o: CheckerContext):
        if node.name not in o.global_funcs:
            raise UndeclaredFunction(node.name)

        param_types, return_type = o.global_funcs[node.name]

        arg_types = []
        for arg in node.args:
            arg_types.append(self.visit(arg, o))

        if len(node.args) != len(param_types):
            raise TypeMismatchInExpression(node)
        
        for i in range(len(param_types)):
            param_type = param_types[i]
            arg = node.args[i]
            arg_type = arg_types[i]

            if isinstance(arg_type, AutoType):
                update_inferred_type(arg, param_type, o)
            else:
                if type(param_type) is not type(arg_type):
                    raise TypeMismatchInExpression(node)
                
                if isinstance(param_type, StructType) and param_type.struct_name != arg_type.struct_name:
                    raise TypeMismatchInExpression(node)
            
        return return_type

    def visit_identifier(self, node: "Identifier", o: CheckerContext):
        for env in reversed(o.local_env):
            if node.name in env:
                return env[node.name]
        
        raise UndeclaredIdentifier(node.name)

    def visit_struct_literal(self, node: "StructLiteral", o: CheckerContext):
        return node

    # Literals
    def visit_int_literal(self, node: "IntLiteral", o: CheckerContext):
        return IntType()

    def visit_float_literal(self, node: "FloatLiteral", o: CheckerContext):
        return FloatType()

    def visit_string_literal(self, node: "StringLiteral", o: CheckerContext):
        return StringType()
