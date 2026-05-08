"""
AST Generation module for TyC programming language.
This module contains the ASTGeneration class that converts parse trees
into Abstract Syntax Trees using the visitor pattern.
"""

from functools import reduce
from build.TyCVisitor import TyCVisitor
from build.TyCParser import TyCParser
from src.utils.nodes import *


class ASTGeneration(TyCVisitor):
    """AST Generation visitor for TyC language."""

    def visitProgram(self, ctx:TyCParser.ProgramContext):
        decls = []
        for child in ctx.children:
            if isinstance(child, TyCParser.Struct_declContext) or isinstance(child, TyCParser.Func_declContext):
                decls.append(self.visit(child))
        return Program(decls)

    def visitStruct_decl(self, ctx: TyCParser.Struct_declContext):
        struct_name = ctx.ID().getText()
        members = []
        if ctx.struct_mem():
            members = [self.visit(member) for member in ctx.struct_mem()]
        return StructDecl(struct_name, members)

    def visitStruct_mem(self, ctx: TyCParser.Struct_memContext):
        member_type = self.visit(ctx.type_())
        member_name = ctx.ID().getText()
        return MemberDecl(member_type, member_name)
    
    def visitFunc_decl(self, ctx: TyCParser.Func_declContext):
        return_type = None
        if ctx.return_type():
            return_type = self.visit(ctx.return_type())
        func_name = ctx.ID().getText()
        params = []
        if ctx.param_list():
            params = self.visit(ctx.param_list())
        body = self.visit(ctx.block_stmt())
        return FuncDecl(return_type, func_name, params, body)
    
    def visitReturn_type(self, ctx: TyCParser.Return_typeContext):
        if ctx.VOID_KW():
            return VoidType()
        else:
            return self.visit(ctx.type_())
    
    def visitParam_list(self, ctx: TyCParser.Param_listContext):
        params = []
        for param in ctx.param():
            params.append(self.visit(param))
        return params
    
    def visitParam(self, ctx: TyCParser.ParamContext):
        param_type = self.visit(ctx.type_())
        param_name = ctx.ID().getText()
        return Param(param_type, param_name)

    def visitType(self, ctx: TyCParser.TypeContext):
        if ctx.INT_KW():
            return IntType()
        elif ctx.FLOAT_KW():
            return FloatType()
        elif ctx.STRING_KW():
            return StringType()
        else:
            return StructType(ctx.ID().getText())
    
    def visitStmt(self, ctx: TyCParser.StmtContext):
        return self.visit(ctx.getChild(0))
    
    def visitExpr_stmt(self, ctx: TyCParser.Expr_stmtContext):
        return ExprStmt(self.visit(ctx.expr()))
    
    def visitVar_dec_stmt(self, ctx: TyCParser.Var_dec_stmtContext):
        if ctx.AUTO():
            var_type = None
        else:
            var_type = self.visit(ctx.type_())
        
        var_name = ctx.ID().getText()

        if ctx.initializer():
            init_value = self.visit(ctx.initializer())
        else:
            init_value = None
        
        return VarDecl(var_type, var_name, init_value)

    def visitInitializer(self, ctx: TyCParser.InitializerContext):
        if ctx.expr():
            return self.visit(ctx.expr())
        else:
            return self.visit(ctx.initializer_list())
        
    def visitInitializer_list(self, ctx: TyCParser.Initializer_listContext):
        initializers = []
        for initializer in ctx.initializer():
            initializers.append(self.visit(initializer))
        return initializers
    
    def visitBlock_stmt(self, ctx: TyCParser.Block_stmtContext):
        stmts = []
        for stmt in ctx.stmt():
            stmts.append(self.visit(stmt))
        return BlockStmt(stmts)

    def visitIf_stmt(self, ctx: TyCParser.If_stmtContext):
        condition = self.visit(ctx.expr())
        if_stmt = self.visit(ctx.stmt(0))
        else_stmt = self.visit(ctx.stmt(1)) if ctx.ELSE() else None
        return IfStmt(condition, if_stmt, else_stmt)

    def visitWhile_stmt(self, ctx: TyCParser.While_stmtContext):
        condition = self.visit(ctx.expr())
        body = self.visit(ctx.stmt())
        return WhileStmt(condition, body)

    def visitFor_stmt(self, ctx: TyCParser.For_stmtContext):
        init = self.visit(ctx.for_init()) if ctx.for_init() else None
        condition = self.visit(ctx.for_condition()) if ctx.for_condition() else None
        update = self.visit(ctx.for_update()) if ctx.for_update() else None
        body = self.visit(ctx.stmt())
        return ForStmt(init, condition, update, body)

    def visitFor_init(self, ctx: TyCParser.For_initContext):
        if ctx.AUTO():
            var_name = ctx.ID().getText()
            init_value = self.visit(ctx.initializer()) if ctx.initializer() else None
            return VarDecl(None, var_name, init_value)
        if ctx.type_():
            var_type = self.visit(ctx.type_())
            var_name = ctx.ID().getText()
            init_value = self.visit(ctx.initializer()) if ctx.initializer() else None
            return VarDecl(var_type, var_name, init_value)

        lhs = self.visit(ctx.lhs())
        rhs = self.visit(ctx.assignment_expr())
        return ExprStmt(AssignExpr(lhs, rhs))

    def visitFor_condition(self, ctx: TyCParser.For_conditionContext):
        return self.visit(ctx.expr())

    def visitFor_update(self, ctx: TyCParser.For_updateContext):
        if ctx.ASSIGN():
            lhs = self.visit(ctx.lhs())
            rhs = self.visit(ctx.assignment_expr())
            return AssignExpr(lhs, rhs)
        if ctx.prefix_expr():
            operator = ctx.INC().getText() if ctx.INC() else ctx.DEC().getText()
            operand = self.visit(ctx.prefix_expr())
            return PrefixOp(operator, operand)
        if ctx.postfix_expr():
            operator = ctx.INC().getText() if ctx.INC() else ctx.DEC().getText()
            operand = self.visit(ctx.postfix_expr())
            return PostfixOp(operator, operand)

    def visitSwitch_stmt(self, ctx: TyCParser.Switch_stmtContext):
        expression = self.visit(ctx.expr())
        case_blocks, default_block = self.visit(ctx.switch_section())
        return SwitchStmt(expression, case_blocks, default_block)
    
    def visitSwitch_section(self, ctx: TyCParser.Switch_sectionContext):
        case_blocks = []
        default_block = None
        if ctx.default_block():
            default_block = self.visit(ctx.default_block())
        for case_block in ctx.case_block():
            case_blocks.append(self.visit(case_block))
        return case_blocks, default_block

    def visitCase_block(self, ctx: TyCParser.Case_blockContext):
        expression = self.visit(ctx.expr())
        stmts = [self.visit(stmt) for stmt in ctx.stmt()]
        return CaseStmt(expression, stmts)

    def visitDefault_block(self, ctx: TyCParser.Default_blockContext):
        stmts = []
        for stmt in ctx.stmt():
            stmts.append(self.visit(stmt))
        return DefaultStmt(stmts)
    
    def visitContinue_stmt(self, ctx: TyCParser.Continue_stmtContext):
        return ContinueStmt()

    def visitReturn_stmt(self, ctx: TyCParser.Return_stmtContext):
        return ReturnStmt(self.visit(ctx.expr())) if ctx.expr() else ReturnStmt()

    def visitBreak_stmt(self, ctx: TyCParser.Break_stmtContext):
        return BreakStmt()
    
    def visitExpr(self, ctx: TyCParser.ExprContext):
        return self.visit(ctx.assignment_expr())

    def visitAssignment_expr(self, ctx: TyCParser.Assignment_exprContext):
        if ctx.assignment_expr() is None:
            return self.visit(ctx.logical_OR_expr())
        
        lhs = self.visit(ctx.lhs())
        rhs = self.visit(ctx.assignment_expr())
        return AssignExpr(lhs, rhs)

    def visitLhs(self, ctx: TyCParser.LhsContext):
        if ctx.MEM_ACCESS() is None:
            return Identifier(ctx.ID().getText())

        return MemberAccess(self.visit(ctx.member_access_expr()), ctx.ID().getText())

    def visitLogical_OR_expr(self, ctx: TyCParser.Logical_OR_exprContext):
        if ctx.logical_OR_expr() is None:
            return self.visit(ctx.logical_AND_expr())
        
        logical_OR_expr = self.visit(ctx.logical_OR_expr())
        logical_AND_expr = self.visit(ctx.logical_AND_expr())
        return BinaryOp(logical_OR_expr, ctx.OR().getText(), logical_AND_expr)

    def visitLogical_AND_expr(self, ctx: TyCParser.Logical_AND_exprContext):
        if ctx.logical_AND_expr() is None:
            return self.visit(ctx.equality_expr())
        
        logical_AND_expr = self.visit(ctx.logical_AND_expr())
        equality_expr = self.visit(ctx.equality_expr())
        return BinaryOp(logical_AND_expr, ctx.AND().getText(), equality_expr)

    def visitEquality_expr(self, ctx: TyCParser.Equality_exprContext):
        if ctx.equality_expr() is None:
            return self.visit(ctx.relational_expr())
        equality_expr = self.visit(ctx.equality_expr())
        relational_expr = self.visit(ctx.relational_expr())
        operation = ctx.EQ() if ctx.EQ() else ctx.NEQ()
        return BinaryOp(equality_expr, operation.getText(), relational_expr)
    
    def visitRelational_expr(self, ctx: TyCParser.Relational_exprContext):
        if ctx.relational_expr() is None:
            return self.visit(ctx.additive_expr())
        
        relational_expr = self.visit(ctx.relational_expr())
        additive_expr = self.visit(ctx.additive_expr())
        operation = ctx.LT() if ctx.LT() else ctx.GT() if ctx.GT() else ctx.LEQ() if ctx.LEQ() else ctx.GEQ()
        return BinaryOp(relational_expr, operation.getText(), additive_expr)

    def visitAdditive_expr(self, ctx: TyCParser.Additive_exprContext):
        if ctx.additive_expr() is None:
            return self.visit(ctx.multiplicative_expr())
        
        additive_expr = self.visit(ctx.additive_expr())
        multiplicative_expr = self.visit(ctx.multiplicative_expr())
        operation = ctx.ADD() if ctx.ADD() else ctx.SUB()
        return BinaryOp(additive_expr, operation.getText(), multiplicative_expr)

    def visitMultiplicative_expr(self, ctx: TyCParser.Multiplicative_exprContext):
        if ctx.multiplicative_expr() is None:
            return self.visit(ctx.unary_expr())
        
        multiplicative_expr = self.visit(ctx.multiplicative_expr())
        unary_expr = self.visit(ctx.unary_expr())
        operation = ctx.MUL() if ctx.MUL() else ctx.DIV() if ctx.DIV() else ctx.MOD()
        return BinaryOp(multiplicative_expr, operation.getText(), unary_expr)

    def visitUnary_expr(self, ctx: TyCParser.Unary_exprContext):
        if ctx.unary_expr() is None:
            return self.visit(ctx.prefix_expr())

        operand = self.visit(ctx.unary_expr())
        operation = ctx.ADD() if ctx.ADD() else ctx.SUB() if ctx.SUB() else ctx.NOT()
        return PrefixOp(operation.getText(), operand)

    def visitPrefix_expr(self, ctx: TyCParser.Prefix_exprContext):
        if ctx.prefix_expr() is None:
            return self.visit(ctx.postfix_expr())
        
        operand = self.visit(ctx.prefix_expr())
        operation = ctx.INC() if ctx.INC() else ctx.DEC()
        return PrefixOp(operation.getText(), operand)
        
    def visitPostfix_expr(self, ctx: TyCParser.Postfix_exprContext):
        if ctx.postfix_expr() is None:
            return self.visit(ctx.member_access_expr())
        
        operand = self.visit(ctx.postfix_expr())
        operation = ctx.INC() if ctx.INC() else ctx.DEC()
        return PostfixOp(operation.getText(), operand)

    def visitMember_access_expr(self, ctx: TyCParser.Member_access_exprContext):
        if ctx.member_access_expr():
            object_expr = self.visit(ctx.member_access_expr())
            member_name = ctx.ID().getText()
            return MemberAccess(object_expr, member_name)
        
        primary_expr = self.visit(ctx.primary_expr())
        if ctx.LPAREN():
            # If it's primary_expr ( arg_list_opt ), then primary_expr must be Identifier
            if isinstance(primary_expr, Identifier):
                func_name = primary_expr.name
                arg_list = self.visit(ctx.arg_list_opt())
                return FuncCall(func_name, arg_list)
            else:
                # This case might not be possible by grammar unless more types are callable
                return primary_expr
        
        return primary_expr

    def visitPrimary_expr(self, ctx: TyCParser.Primary_exprContext):
        if ctx.ID():
            return Identifier(ctx.ID().getText())
        if ctx.literal():
            return self.visit(ctx.literal())
        return self.visit(ctx.expr())

    def visitArg_list_opt(self, ctx: TyCParser.Arg_list_optContext):
        if ctx.arg_list():
            return self.visit(ctx.arg_list())
        return []
    
    def visitArg_list(self, ctx: TyCParser.Arg_listContext):
        if ctx.arg_list() is None:
            return [self.visit(ctx.expr())]
        
        return [self.visit(ctx.expr())] + self.visit(ctx.arg_list())

    def visitLiteral(self, ctx: TyCParser.LiteralContext):
        if ctx.INT():
            return IntLiteral(int(ctx.INT().getText()))
        if ctx.FLOAT():
            return FloatLiteral(float(ctx.FLOAT().getText()))
        if ctx.STRING():
            return StringLiteral(ctx.STRING().getText())
        return self.visit(ctx.struct_lit())
    
    def visitStruct_lit(self, ctx: TyCParser.Struct_litContext):
        return StructLiteral(self.visit(ctx.expr_list_opt()))
    
    def visitExpr_list_opt(self, ctx: TyCParser.Expr_list_optContext):
        if ctx.expr_list():
            return self.visit(ctx.expr_list())
        return []
    
    def visitExpr_list(self, ctx: TyCParser.Expr_listContext):
        if ctx.expr_list() is None:
            return [self.visit(ctx.expr())]
        return [self.visit(ctx.expr())] + self.visit(ctx.expr_list())