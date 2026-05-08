"""
Code generator for TyC.
"""

from typing import Any

from ..utils.nodes import *
from ..utils.visitor import BaseVisitor
from .emitter import *
from .frame import *
from .io import IO_SYMBOL_LIST
from .utils import *


class StringArrayType:
    """Marker type for JVM main(String[] args)."""
    pass


class CodeGenerator(BaseVisitor):
    """Minimal AST -> Jasmin code generator."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.emit = None
        self.functions = {}
        self.structs = {} #BOSUNG
        self.current_return_type = VoidType()
        self.class_name = "TyC"
        self._struct_target = [] # Stack for struct_name
        self._auto_pending = {}  # {var_name: resolved_type} for auto vars with no init

    def _lookup_symbol(self, name: str, sym_list: list[Symbol]) -> Symbol:
        for sym in reversed(sym_list):
            if sym.name == name:
                return sym
        raise RuntimeError(f"Undeclared symbol: {name}")

    def _collect_auto_resolutions(self, stmts, sym_list):
        """
        Pre-pass over a block's statements: for each 'auto var;' with no init,
        find the first assignment and infer its type from the RHS.
        Returns {var_name: resolved_type}.
        """
        resolutions = {}
        temp_sym = list(sym_list)

        for stmt in stmts:
            if isinstance(stmt, VarDecl):
                if stmt.var_type is None and stmt.init_value is None:
                    resolutions[stmt.name] = None  # unresolved yet
                else:
                    t = stmt.var_type or self._infer_type(stmt.init_value, Access(None, temp_sym))
                    temp_sym.append(Symbol(stmt.name, t, Index(len(temp_sym))))

            elif isinstance(stmt, ExprStmt) and isinstance(stmt.expr, AssignExpr):
                lhs = stmt.expr.lhs
                if (isinstance(lhs, Identifier)
                        and lhs.name in resolutions
                        and resolutions[lhs.name] is None):
                    t = self._infer_type(stmt.expr.rhs, Access(None, temp_sym))
                    resolutions[lhs.name] = t
                    temp_sym.append(Symbol(lhs.name, t, Index(len(temp_sym))))

        return {k: v for k, v in resolutions.items() if v is not None}

    def _ends_with_return(self, stmt) -> bool:
        if isinstance(stmt, ReturnStmt):
            return True
        if isinstance(stmt, BlockStmt) and stmt.statements:
            return self._ends_with_return(stmt.statements[-1])
        return False

    def _find_first_return_expr(self, stmt):
        """Scan statement tree for the first return expression."""
        if isinstance(stmt, ReturnStmt):
            return stmt.expr
        if isinstance(stmt, BlockStmt):
            for s in stmt.statements:
                result = self._find_first_return_expr(s)
                if result is not None:
                    return result
        if isinstance(stmt, IfStmt):
            result = self._find_first_return_expr(stmt.then_stmt)
            if result is not None:
                return result
            if stmt.else_stmt:
                return self._find_first_return_expr(stmt.else_stmt)
        if isinstance(stmt, (WhileStmt, ForStmt)):
            return self._find_first_return_expr(stmt.body)
        return None

    def _infer_func_return_type(self, node: FuncDecl) -> Type:
        """Infer return type from first return statement when not declared."""
        param_syms = [Symbol(p.name, p.param_type, Index(i)) for i, p in enumerate(node.params)]
        expr = self._find_first_return_expr(node.body)
        if expr is not None:
            return self._infer_type(expr, Access(None, param_syms))
        return VoidType()

    def _infer_type(self, node: Expr, o: Access):
        if isinstance(node, IntLiteral):
            return IntType()
        if isinstance(node, FloatLiteral):
            return FloatType()
        if isinstance(node, StringLiteral):
            return StringType()
        if isinstance(node, Identifier):
            return self._lookup_symbol(node.name, o.sym).type
        if isinstance(node, AssignExpr):
            return self._infer_type(node.rhs, o)
        if isinstance(node, FuncCall):
            return self.functions[node.name].type.return_type
        if isinstance(node, BinaryOp):
            if node.operator in ["+", "-", "*", "/", "%"]:
                left_type = self._infer_type(node.left, o)
                right_type = self._infer_type(node.right, o)
                if is_float_type(left_type) or is_float_type(right_type):
                    return FloatType()
                return IntType()
            if node.operator in ["<", "<=", ">", ">=", "==", "!="]:
                return IntType()
            if node.operator in ['&&', '||']:
                return IntType()
        if isinstance(node, PrefixOp):
            if node.operator in ['+', '-']:
                return self._infer_type(node.operand, o)
            elif node.operator in ['++', '--', '!']:
                return IntType()
        if isinstance(node, PostfixOp):
            return IntType()
        
        if isinstance(node, MemberAccess):
            obj_type = self._infer_type(node.obj, o)
            struct_name = obj_type.struct_name
            return next(t for name, t in self.structs[struct_name] if name == node.member)
        
        if isinstance(node, StructLiteral):
            if self._struct_target:
                return StructType(self._struct_target[-1])

        return IntType()

    def visit_program(self, node: Program, o: Any = None):
        self.emit = Emitter(f"{self.class_name}.j", self.output_dir)
        self.emit.print_out(self.emit.emit_prolog(self.class_name))

        for io_sym in IO_SYMBOL_LIST:
            self.functions[io_sym.name] = io_sym

        for decl in node.decls:
            if isinstance(decl, StructDecl):
                self.structs[decl.name] = [(m.name, m.member_type) for m in decl.members]
            if isinstance(decl, FuncDecl):
                return_type = decl.return_type if decl.return_type else self._infer_func_return_type(decl)
                param_types = [p.param_type for p in decl.params]
                self.functions[decl.name] = Symbol(
                    decl.name, FunctionType(param_types, return_type), CName(self.class_name)
                )

        for decl in node.decls:
            self.visit(decl, None)

        self.emit.emit_epilog()

    def visit_func_decl(self, node: FuncDecl, o: Any = None):
        self.current_return_type = node.return_type if node.return_type else self._infer_func_return_type(node)
        frame = Frame(node.name, self.current_return_type)
        frame.enter_scope(True)

        if node.name == "main":
            mtype = FunctionType([StringArrayType()], VoidType())
        else:
            mtype = FunctionType([p.param_type for p in node.params], self.current_return_type)

        self.emit.print_out(self.emit.emit_method(node.name, mtype, True))

        start_label = frame.get_start_label()
        end_label = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(start_label, frame))

        local_syms: list[Symbol] = []
        if node.name == "main":
            args_idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(
                    args_idx, "args", StringArrayType(), start_label, end_label
                )
            )

        for param in node.params:
            idx = frame.get_new_index()
            self.emit.print_out(
                self.emit.emit_var(idx, param.name, param.param_type, start_label, end_label)
            )
            local_syms.append(Symbol(param.name, param.param_type, Index(idx)))

        sub_body = SubBody(frame, local_syms)
        self.visit(node.body, sub_body)

        if is_void_type(self.current_return_type):
            self.emit.print_out(self.emit.emit_return(VoidType(), frame))

        self.emit.print_out(self.emit.emit_label(end_label, frame))
        frame.exit_scope()
        self.emit.print_out(self.emit.emit_end_method(frame))

    def visit_block_stmt(self, node: BlockStmt, o: SubBody = None):
        auto_res = self._collect_auto_resolutions(node.statements, o.sym)
        saved_auto = self._auto_pending
        self._auto_pending = {**saved_auto, **auto_res}

        saved_sym_len = len(o.sym)
        for stmt in node.statements:
            o = self.visit(stmt, o)
        del o.sym[saved_sym_len:]

        self._auto_pending = saved_auto
        return o

    def visit_var_decl(self, node: VarDecl, o: SubBody = None):
        frame = o.frame
        idx = frame.get_new_index()
        if node.var_type:
            var_type = node.var_type
        elif node.init_value is not None:
            var_type = self._infer_type(node.init_value, Access(frame, o.sym))
        else:
            var_type = self._auto_pending.get(node.name, IntType())
        self.emit.print_out(
            self.emit.emit_var(
                idx, node.name, var_type, frame.get_start_label(), frame.get_end_label()
            )
        )
        if node.init_value is not None:
            # Push struct_name nếu cần (cho StructLiteral biết target)
            pushed = False
            if is_struct_type(var_type) and isinstance(node.init_value, StructLiteral):
                self._struct_target.append(var_type.struct_name)
                pushed = True
            
            rhs_code, rhs_type = self.visit(node.init_value, Access(frame, o.sym))
            
            if pushed:
                self._struct_target.pop()
            
            if is_float_type(var_type) and is_int_type(rhs_type):
                rhs_code += self.emit.emit_i2f(frame)
            
            self.emit.print_out(rhs_code)
            self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
        else:
            if is_int_type(var_type):
                self.emit.print_out(self.emit.emit_push_iconst(0, frame))

            elif is_float_type(var_type):
                self.emit.print_out(self.emit.emit_push_fconst("0.0", frame))
            
            elif is_string_type(var_type):
                self.emit.print_out(self.emit.emit_push_const("", var_type, frame))

            elif is_struct_type(var_type):
                self.emit.print_out(self.emit.emit_new_instance(var_type.struct_name, frame))
            
            self.emit.print_out(self.emit.emit_write_var(node.name, var_type, idx, frame))
        o.sym.append(Symbol(node.name, var_type, Index(idx)))
        return o

    def visit_expr_stmt(self, node: ExprStmt, o: SubBody = None):
        code, expr_type = self.visit(node.expr, Access(o.frame, o.sym))
        self.emit.print_out(code)
        if not is_void_type(expr_type):
            self.emit.print_out(self.emit.emit_pop(o.frame))
        return o

    def visit_if_stmt(self, node: IfStmt, o: SubBody = None):
        frame = o.frame
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        else_label = frame.get_new_label()
        end_label = frame.get_new_label()
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(else_label, frame))
        self.visit(node.then_stmt, o)
        if not self._ends_with_return(node.then_stmt):
            self.emit.print_out(self.emit.emit_goto(end_label, frame))
        self.emit.print_out(self.emit.emit_label(else_label, frame))
        if node.else_stmt:
            self.visit(node.else_stmt, o)
        self.emit.print_out(self.emit.emit_label(end_label, frame))
        return o

    def visit_while_stmt(self, node: WhileStmt, o: SubBody = None):
        frame = o.frame
        cond_label = frame.get_new_label()
        end_label = frame.get_new_label()

        frame.con_label.append(cond_label)
        frame.brk_label.append(end_label)

        self.emit.print_out(self.emit.emit_label(cond_label, frame))
        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(end_label, frame))
        self.visit(node.body, o)
        self.emit.print_out(self.emit.emit_goto(cond_label, frame))
        self.emit.print_out(self.emit.emit_label(end_label, frame))

        frame.con_label.pop()
        frame.brk_label.pop()
        return o

    def visit_return_stmt(self, node: ReturnStmt, o: SubBody = None):
        frame = o.frame

        if node.expr is None:
            self.emit.print_out(self.emit.emit_return(VoidType(), frame))
            return o
        
        pushed = False
        if is_struct_type(self.current_return_type) and isinstance(node.expr, StructLiteral):
            self._struct_target.append(self.current_return_type.struct_name)
            pushed = True

        return_code, return_type = self.visit(node.expr, Access(frame, o.sym))

        if pushed:
            self._struct_target.pop()

        self.emit.print_out(return_code)
        self.emit.print_out(self.emit.emit_return(return_type, frame))

        return o

    def visit_binary_op(self, node: BinaryOp, o: Access = None):
        left_code, left_type = self.visit(node.left, o)
        right_code, right_type = self.visit(node.right, o)
        frame = o.frame

        if node.operator in ['+', '-', '*', '/']:
            result_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()

            if is_float_type(result_type):
                if is_int_type(left_type):
                    left_code += self.emit.emit_i2f(frame)
                if is_int_type(right_type):
                    right_code += self.emit.emit_i2f(frame)
            
            if node.operator in ['+', '-']:
                return (left_code + right_code + self.emit.emit_add_op(node.operator, result_type, frame), result_type)
            
            if node.operator in ['*', '/']:
                return (left_code + right_code + self.emit.emit_mul_op(node.operator, result_type, frame), result_type)

        if node.operator == "%":
            return left_code + right_code + self.emit.emit_mod(frame), IntType()
        if node.operator in ["<", "<=", ">", ">=", "==", "!="]:
            op_type = FloatType() if is_float_type(left_type) or is_float_type(right_type) else IntType()
            if is_float_type(op_type):
                if is_int_type(left_type):
                    left_code += self.emit.emit_i2f(frame)
                if is_int_type(right_type):
                    right_code += self.emit.emit_i2f(frame)
            return left_code + right_code + self.emit.emit_re_op(node.operator, op_type, frame), IntType()
        if node.operator == '||':
            true_label = frame.get_new_label()
            end_label = frame.get_new_label()
            code = (
                left_code
                + self.emit.emit_if_true(true_label, frame)
                + right_code
                + self.emit.emit_if_true(true_label, frame)
                + self.emit.emit_push_iconst(0, frame)
                + self.emit.emit_goto(end_label, frame)
                + self.emit.emit_label(true_label, frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_label(end_label, frame)
            )
            return code, IntType()

        if node.operator == '&&':
            false_label = frame.get_new_label()
            end_label = frame.get_new_label()
            code = (
                left_code
                + self.emit.emit_if_false(false_label, frame)
                + right_code
                + self.emit.emit_if_false(false_label, frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_goto(end_label, frame)
                + self.emit.emit_label(false_label, frame)
                + self.emit.emit_push_iconst(0, frame)
                + self.emit.emit_label(end_label, frame)
            )
            return code, IntType()

        raise RuntimeError(f"Unsupported operator: {node.operator}")

    def visit_assign_expr(self, node: AssignExpr, o: Access = None):
        frame = o.frame
        
        if isinstance(node.lhs, Identifier):
            lhs_sym = self._lookup_symbol(node.lhs.name, o.sym)
            lhs_type = lhs_sym.type
        else:
            obj_code, obj_type = self.visit(node.lhs.obj, o)
            struct_name = obj_type.struct_name
            lhs_type = next(t for name, t in self.structs[struct_name] if name == node.lhs.member)

        pushed = False
        if is_struct_type(lhs_type) and isinstance(node.rhs, StructLiteral):
            self._struct_target.append(lhs_type.struct_name)
            pushed = True
        
        rhs_code, rhs_type = self.visit(node.rhs, o)

        if pushed:
            self._struct_target.pop()
        
        if is_float_type(lhs_type) and is_int_type(rhs_type):
            rhs_code += self.emit.emit_i2f(frame)

        if isinstance(node.lhs, Identifier):
            idx = lhs_sym.value.value
            code = (
                rhs_code
                + self.emit.emit_dup(frame)
                + self.emit.emit_write_var(node.lhs.name, lhs_type, idx, frame)
            )
            return code, lhs_type

        else:
            field_name = node.lhs.member
            field_lexeme = f'{struct_name}/{field_name}'

            code = (
                obj_code
                + rhs_code
                + self.emit.emit_dup_x1(frame)
                + self.emit.emit_put_field(field_lexeme, lhs_type, frame)
            )
            return code, lhs_type

    def visit_func_call(self, node: FuncCall, o: Access = None):
        frame = o.frame
        fn_sym = self.functions[node.name]
        fn_type = fn_sym.type
        code = ""

        for i, arg in enumerate(node.args):
            param_type = fn_type.param_types[i]
            pushed = False
            if is_struct_type(param_type) and isinstance(arg, StructLiteral):
                self._struct_target.append(param_type.struct_name)
                pushed = True

            arg_code, _ = self.visit(arg, o)

            if pushed:
                self._struct_target.pop()

            code += arg_code
        code += self.emit.emit_invoke_static(f"{fn_sym.value.value}/{node.name}", fn_type, frame)
        return code, fn_type.return_type

    def visit_identifier(self, node: Identifier, o: Access = None):
        sym = self._lookup_symbol(node.name, o.sym)
        return self.emit.emit_read_var(node.name, sym.type, sym.value.value, o.frame), sym.type

    def visit_int_literal(self, node: IntLiteral, o: Access = None):
        return self.emit.emit_push_iconst(node.value, o.frame), IntType()

    def visit_float_literal(self, node: FloatLiteral, o: Access = None):
        return self.emit.emit_push_fconst(str(node.value), o.frame), FloatType()

    def visit_string_literal(self, node: StringLiteral, o: Access = None):
        return self.emit.emit_push_const(node.value, StringType(), o.frame), StringType()

    def visit_struct_decl(self, node: StructDecl, o: Any = None):
        # Create Struct Emitter
        struct_emitter = Emitter(f'{node.name}.j', self.output_dir)

        # Prolog - class header
        struct_emitter.print_out(struct_emitter.emit_prolog(node.name))

        # Emit members
        for member in node.members:
            jvm_type = struct_emitter.get_jvm_type(member.member_type)
            struct_emitter.print_out(f'.field public {member.name} {jvm_type}\n')
        
        # Constructor
        max_stack = 1
        for member in node.members:
            if is_string_type(member.member_type):
                max_stack = max(max_stack, 2)
            elif is_struct_type(member.member_type):
                max_stack = max(max_stack, 3)

        struct_emitter.print_out(".method public <init>()V\n")
        struct_emitter.print_out(struct_emitter.jvm.emitLIMITSTACK(max_stack))
        struct_emitter.print_out(struct_emitter.jvm.emitLIMITLOCAL(1))
        struct_emitter.print_out(struct_emitter.jvm.emitALOAD(0))
        struct_emitter.print_out(struct_emitter.jvm.emitINVOKESPECIAL("java/lang/Object/<init>", "()V"))

        for member in node.members:
            jvm_member_type = struct_emitter.get_jvm_type(member.member_type)
            if is_string_type(member.member_type):
                struct_emitter.print_out(struct_emitter.jvm.emitALOAD(0))
                struct_emitter.print_out(struct_emitter.jvm.emitLDC('""'))
                struct_emitter.print_out(struct_emitter.jvm.emitPUTFIELD(f'{node.name}/{member.name}', jvm_member_type))
            elif is_struct_type(member.member_type):
                inner = member.member_type.struct_name
                struct_emitter.print_out(struct_emitter.jvm.emitALOAD(0))
                struct_emitter.print_out(struct_emitter.jvm.emitNEW(inner))
                struct_emitter.print_out(struct_emitter.jvm.emitDUP())
                struct_emitter.print_out(struct_emitter.jvm.emitINVOKESPECIAL(f'{inner}/<init>', "()V"))
                struct_emitter.print_out(struct_emitter.jvm.emitPUTFIELD(f'{node.name}/{member.name}', jvm_member_type))

        struct_emitter.print_out(struct_emitter.jvm.emitRETURN())
        struct_emitter.print_out(struct_emitter.jvm.emitENDMETHOD())

        # Epilog - close class
        struct_emitter.emit_epilog()

    def visit_member_decl(self, node: MemberDecl, o: Any = None):
        return None

    def visit_param(self, node: Param, o: Any = None):
        return None

    def visit_int_type(self, node: IntType, o: Any = None):
        return node

    def visit_float_type(self, node: FloatType, o: Any = None):
        return node

    def visit_string_type(self, node: StringType, o: Any = None):
        return node

    def visit_void_type(self, node: VoidType, o: Any = None):
        return node

    def visit_struct_type(self, node: StructType, o: Any = None):
        return node

    def visit_for_stmt(self, node: ForStmt, o: Any = None):
        frame = o.frame

        # Emit Init (VarDecl or ExprStmt)
        if node.init:
            o = self.visit(node.init, o)

        cond_label = frame.get_new_label()
        update_label = frame.get_new_label()
        end_label = frame.get_new_label()

        # Push continue and break labels to frame before visit body
        frame.con_label.append(update_label)
        frame.brk_label.append(end_label)

        # Emit Condition  
        self.emit.print_out(self.emit.emit_label(cond_label, frame))
        if node.condition:
            cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
            self.emit.print_out(cond_code)
            self.emit.print_out(self.emit.emit_if_false(end_label, frame))
        
        # Emit Body
        self.visit(node.body, o)

        # Emit Update (continue jumps to here)
        self.emit.print_out(self.emit.emit_label(update_label, frame))
        if node.update:
            update_code, update_type = self.visit(node.update, Access(frame, o.sym))
            self.emit.print_out(update_code)
            if not is_void_type(update_type):
                self.emit.print_out(self.emit.emit_pop(frame))

        # Return to condition_label
        self.emit.print_out(self.emit.emit_goto(cond_label, frame))

        # Emit End label
        self.emit.print_out(self.emit.emit_label(end_label, frame))

        frame.con_label.pop()
        frame.brk_label.pop()

        return o
        

    def visit_switch_stmt(self, node: SwitchStmt, o: Any = None):
        frame = o.frame
        
        # Evaluate switch expression -> Store to a temp var
        expr_code, _ = self.visit(node.expr, Access(frame, o.sym))
        self.emit.print_out(expr_code)
        temp_idx = frame.get_new_index()
        self.emit.print_out(self.emit.emit_write_var('switch_expr_val', IntType(), temp_idx, frame))

        # Create labels for each case and default
        case_labels = [frame.get_new_label() for _ in node.cases]
        default_label = frame.get_new_label()
        end_label = frame.get_new_label()

        # Push break label before visit body
        frame.brk_label.append(end_label)

        # Dispatch table
        for i, case in enumerate(node.cases):
            self.emit.print_out(self.emit.emit_read_var('switch_expr_val', IntType(), temp_idx, frame))
            case_val_code, _ = self.visit(case.expr, Access(frame, o.sym))
            self.emit.print_out(case_val_code)
            self.emit.print_out(self.emit.emit_re_op('==', IntType(), frame))
            self.emit.print_out(self.emit.emit_if_true(case_labels[i], frame))

        self.emit.print_out(self.emit.emit_goto(default_label, frame))

        # Emit each case
        saved_sym_len = len(o.sym)
        for i, case in enumerate(node.cases):
            self.emit.print_out(self.emit.emit_label(case_labels[i], frame))
            for stmt in case.statements:
                o = self.visit(stmt, o)
        
        # Emit default case
        self.emit.print_out(self.emit.emit_label(default_label, frame))
        if node.default_case:
            for stmt in node.default_case.statements:
                o = self.visit(stmt, o)
            
        del o.sym[saved_sym_len:]
        
        # Emit end label
        self.emit.print_out(self.emit.emit_label(end_label, frame))

        frame.brk_label.pop()

        return o
        

    def visit_case_stmt(self, node: CaseStmt, o: Any = None):
        return None

    def visit_default_stmt(self, node: DefaultStmt, o: Any = None):
        return None

    def visit_break_stmt(self, node: BreakStmt, o: Any = None):
        self.emit.print_out(self.emit.emit_goto(o.frame.get_break_label(), o.frame))
        return o

    def visit_continue_stmt(self, node: ContinueStmt, o: Any = None):
        self.emit.print_out(self.emit.emit_goto(o.frame.get_continue_label(), o.frame))
        return o

    def visit_prefix_op(self, node: PrefixOp, o: Access = None):
        operand_code, operand_type = self.visit(node.operand, o)
        frame = o.frame

        if node.operator in ['+', '-']:
            result_type = FloatType() if is_float_type(operand_type) else IntType()
            if node.operator == '+':
                return (operand_code, result_type)
            else:
                return (operand_code + self.emit.emit_neg_op(result_type, frame), result_type)
        
        if node.operator == '!':
            true_label = frame.get_new_label()
            end_label = frame.get_new_label()
            not_code = (
                operand_code
                + self.emit.emit_if_false(true_label, frame)
                + self.emit.emit_push_iconst(0, frame)
                + self.emit.emit_goto(end_label, frame)
                + self.emit.emit_label(true_label, frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_label(end_label, frame)
            )
            return not_code, IntType()

        if node.operator in ['++', '--']:
            if isinstance(node.operand, Identifier):
                sym = self._lookup_symbol(node.operand.name, o.sym)
                idx = sym.value.value
                inc_dec_code = (
                    self.emit.emit_read_var(node.operand.name, sym.type, idx, frame)
                    + self.emit.emit_push_iconst(1, frame)
                    + self.emit.emit_add_op('+' if node.operator == '++' else '-', sym.type, frame)
                    + self.emit.emit_dup(frame)
                    + self.emit.emit_write_var(node.operand.name, sym.type, idx, frame)
                )
                return inc_dec_code, IntType()
            
            elif isinstance(node.operand, MemberAccess):
                obj_code, obj_type = self.visit(node.operand.obj, o)
                struct_name = obj_type.struct_name

                field_type = next(t for name, t in self.structs[struct_name] if name == node.operand.member)
                field_lexeme = f'{struct_name}/{node.operand.member}'

                inc_dec_code = (
                    obj_code
                    + self.emit.emit_dup(frame)
                    + self.emit.emit_get_field(field_lexeme, field_type, frame)
                    + self.emit.emit_push_iconst(1, frame)
                    + self.emit.emit_add_op('+' if node.operator == '++' else '-', field_type, frame)
                    + self.emit.emit_dup_x1(frame)
                    + self.emit.emit_put_field(field_lexeme, field_type, frame)
                )
                return inc_dec_code, IntType()
            
        else:
            raise IllegalOperandException(f"Invalid operand for prefix operator: {node.operator}")
        
    def visit_postfix_op(self, node: PostfixOp, o: Any = None):
        operand_code, operand_type = self.visit(node.operand, o)
        frame = o.frame

        if isinstance(node.operand, Identifier):
            sym = self._lookup_symbol(node.operand.name, o.sym)
            idx = sym.value.value

            code = (
                self.emit.emit_read_var(node.operand.name, sym.type, idx, frame)
                + self.emit.emit_dup(frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_add_op('+' if node.operator == '++' else '-', sym.type, frame)
                + self.emit.emit_write_var(node.operand.name, sym.type, idx, frame)
            )
            return code, IntType()
        
        elif isinstance(node.operand, MemberAccess):
            obj_code, obj_type = self.visit(node.operand.obj, o)
            struct_name = obj_type.struct_name
            
            field_type = next(t for name, t in self.structs[struct_name] if name == node.operand.member)
            field_lexeme = f'{struct_name}/{node.operand.member}'

            code = (
                obj_code
                + self.emit.emit_dup(frame)
                + self.emit.emit_get_field(field_lexeme, field_type, frame)
                + self.emit.emit_dup_x1(frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_add_op('+' if node.operator == '++' else '-', field_type, frame)
                + self.emit.emit_put_field(field_lexeme, field_type, frame)
            )
            return code, IntType()
        
        else:
            raise IllegalOperandException(f"Invalid operand for postfix operator: {node.operator}")

    def visit_member_access(self, node: MemberAccess, o: Any = None):
        frame = o.frame
        obj_code, obj_type = self.visit(node.obj, o)

        struct_name = obj_type.struct_name
        field_type = next(t for name, t in self.structs[struct_name] if name == node.member)
        field_lexeme = f"{struct_name}/{node.member}"

        code = obj_code + self.emit.emit_get_field(field_lexeme, field_type, frame)
        return code, field_type

    def visit_struct_literal(self, node: StructLiteral, o: Any = None):
        struct_name = self._struct_target[-1]
        frame = o.frame
        fields = self.structs[struct_name]

        # New + <init> -> Stack: obj
        code = self.emit.emit_new_instance(struct_name, frame)

        # Init each field
        for i, value_expr in enumerate(node.values):
            field_name, field_type = fields[i]

            code += self.emit.emit_dup(frame)

            # Nested StructLiteral
            nested_pushed = False
            if is_struct_type(field_type) and isinstance(value_expr, StructLiteral):
                self._struct_target.append(field_type.struct_name)
                nested_pushed = True

            val_code, val_type = self.visit(value_expr, o)

            if nested_pushed:
                self._struct_target.pop()

            if is_float_type(field_type) and is_int_type(val_type):
                val_code += self.emit.emit_i2f(frame)
            
            code += val_code
            code += self.emit.emit_put_field(f'{struct_name}/{field_name}', field_type, frame)
        
        return code, StructType(struct_name)
