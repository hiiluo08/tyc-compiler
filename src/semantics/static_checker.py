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
        return visitor.auto_type(self, o)

    def __str__(self):
        return "AutoType()"

class CheckerContext:
    def __init__(self):
        self.local_env = [{}]
        self.global_funcs = {}
        self.global_structs = {}
        self.control_stack = []
        self.current_func_return_type = None
        self.current_func_name = None
        self.current_func_params = []
    
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
                return True
    return False

class StaticChecker(ASTVisitor):
    def _is_const_int_expr(self, expr):
        if isinstance(expr, IntLiteral):
            return True
        if isinstance(expr, PrefixOp):
            if expr.operator in ['+', '-', '!']:
                return self._is_const_int_expr(expr.operand)
            return False
        if isinstance(expr, BinaryOp):
            int_ops = ['+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '&&', '||']
            if expr.operator in int_ops:
                return (self._is_const_int_expr(expr.left) and self._is_const_int_expr(expr.right))
            return False
        return False         

    def _infer_struct_literal(self, struct_name: str, literal: "StructLiteral", o: CheckerContext):
        struct_fields = o.global_structs[struct_name]
        if len(literal.values) != len(struct_fields):
            return False
        for field_type, val in zip(struct_fields.values(), literal.values):
            val_type = self.visit(val, o)
            if isinstance(field_type, StructType):
                if isinstance(val_type, StructType):
                    if field_type.struct_name != val_type.struct_name:
                        return False
                elif isinstance(val_type, StructLiteral):
                    if not self._infer_struct_literal(field_type.struct_name, val, o):
                        return False
                elif isinstance(val_type, AutoType):
                    if not update_inferred_type(val, field_type, o):
                        return False
                else:
                    return False
            
            else:
                if isinstance(val_type, AutoType):
                    if not update_inferred_type(val, field_type, o):
                        return False
                elif isinstance(val_type, StructType) or isinstance(val_type, StructLiteral):
                    return False
                elif type(field_type) != type(val_type):
                    return False
        return True

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
            if isinstance(member_type, StructType):
                if member_type.struct_name not in o.global_structs:
                    raise UndeclaredStruct(member_type.struct_name)
                if member_type.struct_name == node.name:
                    raise UndeclaredStruct(member_type.struct_name)
                    
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
            o.current_func_params = [p.name for p in node.params]
            self.visit(stmt, o)
            o.current_func_params = []
        
        if isinstance(o.current_func_return_type, AutoType):
            o.current_func_return_type = VoidType()
            o.global_funcs[node.name] = (param_types, VoidType())
        
        for var_type in o.local_env[-1].values():
            if isinstance(var_type, AutoType):
                raise TypeCannotBeInferred(node.body)

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
        
        for var_type in o.local_env[-1].values():
            if isinstance(var_type, AutoType):
                raise TypeCannotBeInferred(node)

        o.pop_scope()

    def visit_var_decl(self, node: "VarDecl", o: CheckerContext):
        if node.name in o.local_env[-1]:
            raise Redeclared('Variable', node.name)

        if node.name in o.current_func_params:
            raise Redeclared('Variable', node.name)

        lhs_type = self.visit(node.var_type, o) if node.var_type else AutoType()

        if isinstance(lhs_type, StructType):
            if lhs_type.struct_name not in o.global_structs:
                raise UndeclaredStruct(lhs_type.struct_name)

        if node.init_value:
            rhs_type = self.visit(node.init_value, o)

            if isinstance(lhs_type, AutoType):
                if isinstance(rhs_type, AutoType) or isinstance(rhs_type, StructLiteral):
                    raise TypeCannotBeInferred(node)
                else:
                    lhs_type = rhs_type
            
            elif isinstance(lhs_type, StructType):
                if isinstance(rhs_type, StructType):
                    if lhs_type.struct_name != rhs_type.struct_name:
                        raise TypeMismatchInStatement(node)
                
                elif isinstance(rhs_type, AutoType):
                    if not update_inferred_type(node.init_value, lhs_type, o):
                        raise TypeCannotBeInferred(node.init_value)
                    rhs_type = lhs_type
                
                elif isinstance(rhs_type, StructLiteral):
                    if not self._infer_struct_literal(lhs_type.struct_name, node.init_value, o):
                        raise TypeMismatchInExpression(node.init_value)

                else:
                    raise TypeMismatchInStatement(node)
            
            else:
                if isinstance(rhs_type, StructType) or isinstance(rhs_type, StructLiteral):
                    raise TypeMismatchInStatement(node)

                elif isinstance(rhs_type, AutoType):
                    if not update_inferred_type(node.init_value, lhs_type, o):
                        raise TypeCannotBeInferred(node.init_value)
                    rhs_type = lhs_type

                else:
                    if type(lhs_type) != type(rhs_type):
                        raise TypeMismatchInStatement(node)

        o.local_env[-1][node.name] = lhs_type 


    def visit_if_stmt(self, node: "IfStmt", o: CheckerContext):
        condition_type = self.visit(node.condition, o)
        if isinstance(condition_type, AutoType):
            if not update_inferred_type(node.condition, IntType(), o):
                raise TypeCannotBeInferred(node.condition)
        elif not isinstance(condition_type, IntType):
            raise TypeMismatchInStatement(node)

        o.push_scope()
        self.visit(node.then_stmt, o)
        o.pop_scope()
        
        if node.else_stmt:
            o.push_scope()
            self.visit(node.else_stmt, o)
            o.pop_scope()

    def visit_while_stmt(self, node: "WhileStmt", o: CheckerContext):
        o.control_stack.append('loop')

        condition_type = self.visit(node.condition, o)
        if isinstance(condition_type, AutoType):
            if not update_inferred_type(node.condition, IntType(), o):
                raise TypeCannotBeInferred(node.condition)
        elif not isinstance(condition_type, IntType):
            raise TypeMismatchInStatement(node)
        
        o.push_scope()
        self.visit(node.body, o)
        o.pop_scope()
        
        o.control_stack.pop()

    def visit_for_stmt(self, node: "ForStmt", o: CheckerContext):
        o.control_stack.append('loop')

        if node.init:
            self.visit(node.init, o)
        
        if node.condition:
            condition_type = self.visit(node.condition, o)
            if isinstance(condition_type, AutoType):
                if not update_inferred_type(node.condition, IntType(), o):
                    raise TypeCannotBeInferred(node.condition)
            elif not isinstance(condition_type, IntType):
                raise TypeMismatchInStatement(node)
        
        if node.update:
            self.visit(node.update, o)
        
        if isinstance(node.body, BlockStmt):
            self.visit(node.body, o)
        else:
            o.push_scope()
            self.visit(node.body, o)
            o.pop_scope()

        o.control_stack.pop()
        

    def visit_switch_stmt(self, node: "SwitchStmt", o: CheckerContext):
        o.control_stack.append('switch')

        expr_type = self.visit(node.expr, o)
        if isinstance(expr_type, AutoType):
            if not update_inferred_type(node.expr, IntType(), o):
                raise TypeCannotBeInferred(node.expr)
        elif not isinstance(expr_type, IntType):
            raise TypeMismatchInStatement(node)

        o.push_scope()
        for case in node.cases:
            self.visit(case, o)
            # try: 
            #     self.visit(case, o)
            # except TypeMismatchInStatement as e:
            #     if e.stmt is case:
            #         raise TypeMismatchInStatement(node)
            #     raise
            
        
        if node.default_case:
            self.visit(node.default_case, o)
            # try:
            #     self.visit(node.default_case, o)
            # except TypeMismatchInStatement as e:
            #     if e.stmt is node.default_case:
            #         raise TypeMismatchInStatement(node)
            #     raise
        
        for var_type in o.local_env[-1].values():
            if isinstance(var_type, AutoType):
                raise TypeCannotBeInferred(node)

        o.pop_scope()

        o.control_stack.pop()

    def visit_case_stmt(self, node: "CaseStmt", o: CheckerContext):
        case_type = self.visit(node.expr, o)

        if not self._is_const_int_expr(node.expr):
            raise TypeMismatchInStatement(node)

        if not isinstance(case_type, IntType):
            raise TypeMismatchInStatement(node)

        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_default_stmt(self, node: "DefaultStmt", o: CheckerContext):
        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_break_stmt(self, node: "BreakStmt", o: CheckerContext):
        if o.control_stack:
            return
        raise MustInLoop(node)

    def visit_continue_stmt(self, node: "ContinueStmt", o: CheckerContext):
        if 'loop' in o.control_stack:
            return
        raise MustInLoop(node)

    def visit_return_stmt(self, node: "ReturnStmt", o: CheckerContext):
        if isinstance(o.current_func_return_type, VoidType):
            if node.expr:
                raise TypeMismatchInStatement(node)
            return
        else:
            if not node.expr:
                if isinstance(o.current_func_return_type, AutoType):
                    return  # bare return in auto function → infer void at end of func
                raise TypeMismatchInStatement(node)
        
        return_type = self.visit(node.expr, o)
        
        if isinstance(o.current_func_return_type, AutoType):
            if isinstance(return_type, AutoType) or isinstance(return_type, StructLiteral):
                raise TypeCannotBeInferred(node)
            o.current_func_return_type = return_type
            param_types, _ = o.global_funcs[o.current_func_name]
            o.global_funcs[o.current_func_name] = (param_types, return_type)

        elif isinstance(o.current_func_return_type, StructType):
            if isinstance(return_type, StructLiteral):
                if not self._infer_struct_literal(o.current_func_return_type.struct_name, return_type, o):
                    raise TypeMismatchInStatement(node)
            elif isinstance(return_type, StructType):
                if return_type.struct_name != o.current_func_return_type.struct_name:
                    raise TypeMismatchInStatement(node)
            elif isinstance(return_type, AutoType):
                if not update_inferred_type(node.expr, o.current_func_return_type, o):
                    raise TypeCannotBeInferred(node.expr)
                return
            else:
                raise TypeMismatchInStatement(node)
            
        else:
            if isinstance(return_type, AutoType):
                if not update_inferred_type(node.expr, o.current_func_return_type, o):
                    raise TypeCannotBeInferred(node.expr)
                return
            if type(return_type) != type(o.current_func_return_type):
                raise TypeMismatchInStatement(node)

    def visit_expr_stmt(self, node: "ExprStmt", o: CheckerContext):
        if isinstance(node.expr, AssignExpr):
            try:
                self.visit(node.expr, o)
            except TypeMismatchInExpression as e:
                if e.expr is node.expr:
                    raise TypeMismatchInStatement(node)
                raise
        else:
            expr_type = self.visit(node.expr, o)
            if isinstance(expr_type, AutoType):
                raise TypeCannotBeInferred(node)

    # Expressions
    def visit_binary_op(self, node: "BinaryOp", o: CheckerContext):
        lhs_type = self.visit(node.left, o)
        rhs_type = self.visit(node.right, o)

        arithmetic_op = ['+', '-', '*', '/']
        relational_op = ['==', '!=', '<', '<=', '>', '>=']
        logical_op = ['&&', '||']
        num_type = (IntType, FloatType)

        if isinstance(lhs_type, AutoType) or isinstance(rhs_type, AutoType):
            if node.operator in arithmetic_op:
                if isinstance(node.left, IntLiteral):
                    if not update_inferred_type(node.right, IntType(), o):
                        raise TypeCannotBeInferred(node.right)
                    rhs_type = IntType()
                elif isinstance(node.right, IntLiteral):
                    if not update_inferred_type(node.left, IntType(), o):
                        raise TypeCannotBeInferred(node.left)
                    lhs_type = IntType()
                else:
                    raise TypeCannotBeInferred(node)
            elif node.operator in relational_op:
                raise TypeCannotBeInferred(node)
            elif node.operator in logical_op or node.operator == '%':
                if isinstance(lhs_type, AutoType):
                    if not update_inferred_type(node.left, IntType(), o):
                        raise TypeCannotBeInferred(node.left)
                    lhs_type = IntType()
                if isinstance(rhs_type, AutoType):
                    if not update_inferred_type(node.right, IntType(), o):
                        raise TypeCannotBeInferred(node.right)
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
            if isinstance(lhs_type, AutoType):
                if isinstance(rhs_type, StructLiteral) or isinstance(rhs_type, AutoType):
                    raise TypeCannotBeInferred(node)
                else:
                    if not update_inferred_type(node.lhs, rhs_type, o):
                        raise TypeCannotBeInferred(node.lhs)
                    lhs_type = rhs_type
                
            elif isinstance(lhs_type, StructType):
                if isinstance(rhs_type, AutoType):
                    if not update_inferred_type(node.rhs, lhs_type, o):
                        raise TypeCannotBeInferred(node.rhs)
                    rhs_type = lhs_type
                elif isinstance(rhs_type, StructType):
                    if lhs_type.struct_name != rhs_type.struct_name:
                        raise TypeMismatchInExpression(node)
                elif isinstance(rhs_type, StructLiteral):
                    if not self._infer_struct_literal(lhs_type.struct_name, node.rhs, o):
                        raise TypeMismatchInExpression(node.rhs)

                else:
                    raise TypeMismatchInExpression(node)
            
            else:
                if isinstance(rhs_type, AutoType):
                    if not update_inferred_type(node.rhs, lhs_type, o):
                        raise TypeCannotBeInferred(node.rhs)
                    rhs_type = lhs_type
                
                elif isinstance(rhs_type, StructType) or isinstance(rhs_type, StructLiteral):
                    raise TypeMismatchInExpression(node)
                
                elif type(lhs_type) != type(rhs_type):
                    raise TypeMismatchInExpression(node)
            
            return lhs_type

        raise TypeMismatchInExpression(node)

    def visit_member_access(self, node: "MemberAccess", o: CheckerContext):
        obj_type = self.visit(node.obj, o)

        if isinstance(obj_type, AutoType):
            raise TypeCannotBeInferred(node)
        
        if not isinstance(obj_type, StructType):
            raise TypeMismatchInExpression(node)
        
        struct_fields = o.global_structs[obj_type.struct_name]
        if node.member not in struct_fields:
            raise TypeMismatchInExpression(node)
        
        return struct_fields[node.member]

    def visit_func_call(self, node: "FuncCall", o: CheckerContext):
        if node.name not in o.global_funcs:
            raise UndeclaredFunction(node.name)

        param_types, return_type = o.global_funcs[node.name]

        for arg in node.args:
            self.visit(arg, o)

        if len(node.args) != len(param_types):
            raise TypeMismatchInExpression(node)

        for param_type, arg in zip(param_types, node.args):
            arg_type = self.visit(arg, o)

            if isinstance(arg_type, AutoType):
                if not update_inferred_type(arg, param_type, o):
                    raise TypeCannotBeInferred(arg)
                arg_type = param_type
            
            elif isinstance(arg_type, StructType):
                if not isinstance(param_type, StructType):
                    raise TypeMismatchInExpression(node)
                if arg_type.struct_name != param_type.struct_name:
                    raise TypeMismatchInExpression(node)
            
            elif isinstance(arg_type, StructLiteral):
                if not isinstance(param_type, StructType):
                    raise TypeMismatchInExpression(node)
                if not self._infer_struct_literal(param_type.struct_name, arg, o):
                    raise TypeMismatchInExpression(node)
                
            else:
                if type(param_type) != type(arg_type):
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
