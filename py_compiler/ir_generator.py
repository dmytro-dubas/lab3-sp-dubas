from typing import List, Optional, Any
from dataclasses import dataclass
from .ast_nodes import (
    ASTNode, Program, FunctionDef, Param, VarDecl, CompoundStmt,
    ExprStmt, IfStmt, WhileStmt, ForStmt, ReturnStmt,
    AssignExpr, BinaryOp, UnaryOp, FuncCall, Identifier, Literal
)

@dataclass
class TACInstruction:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None

    def __str__(self) -> str:
        if self.op == "LABEL":
            return f"{self.result}:"
        elif self.op == "FUNC_BEGIN":
            return f"\nfunc_{self.result}:"
        elif self.op == "FUNC_END":
            return ""
        elif self.op == "ASSIGN":
            return f"  {self.result} = {self.arg1}"
        elif self.op in ("+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=", "&&", "||"):
            return f"  {self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op in ("NEG", "NOT", "POS"):
            op_sym = "-" if self.op == "NEG" else ("!" if self.op == "NOT" else "+")
            return f"  {self.result} = {op_sym}{self.arg1}"
        elif self.op == "GOTO":
            return f"  goto {self.result}"
        elif self.op == "IF_FALSE":
            return f"  if_false {self.arg1} goto {self.result}"
        elif self.op == "IF_TRUE":
            return f"  if_true {self.arg1} goto {self.result}"
        elif self.op == "PARAM":
            return f"  param {self.arg1}"
        elif self.op == "CALL":
            if self.result:
                return f"  {self.result} = call {self.arg1}, {self.arg2}"
            return f"  call {self.arg1}, {self.arg2}"
        elif self.op == "RETURN":
            if self.arg1:
                return f"  return {self.arg1}"
            return "  return"
        return f"  {self.op} {self.arg1} {self.arg2} -> {self.result}"


class IRGenerator:

    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self._temp_counter = 0
        self._label_counter = 0

    def new_temp(self) -> str:
        self._temp_counter += 1
        return f"t{self._temp_counter}"

    def new_label(self, prefix: str = "L") -> str:
        self._label_counter += 1
        return f"{prefix}_{self._label_counter}"

    def emit(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None):
        self.instructions.append(TACInstruction(op=op, arg1=arg1, arg2=arg2, result=result))

    def generate(self, program: Program) -> List[TACInstruction]:
        self.instructions.clear()
        self._temp_counter = 0
        self._label_counter = 0

        for decl in program.declarations:
            if isinstance(decl, VarDecl):
                if decl.init_expr:
                    val = self._gen_expr(decl.init_expr)
                    self.emit("ASSIGN", arg1=val, result=decl.var_name)
            elif isinstance(decl, FunctionDef):
                self._gen_function(decl)

        return self.instructions

    def get_listing(self) -> str:
        return "\n".join(str(instr) for instr in self.instructions)

    def _gen_function(self, func: FunctionDef):
        self.emit("FUNC_BEGIN", result=func.name)

        for idx, p in enumerate(func.params):
            self.emit("ASSIGN", arg1=f"arg_{idx}", result=p.name)

        if func.body:
            self._gen_compound(func.body)

        if not (self.instructions and self.instructions[-1].op == "RETURN"):
            self.emit("RETURN", arg1="0")
        self.emit("FUNC_END", result=func.name)

    def _gen_compound(self, block: CompoundStmt):
        for stmt in block.statements:
            self._gen_stmt(stmt)

    def _gen_stmt(self, stmt: ASTNode):
        if isinstance(stmt, CompoundStmt):
            self._gen_compound(stmt)
        elif isinstance(stmt, VarDecl):
            if stmt.init_expr:
                val = self._gen_expr(stmt.init_expr)
                self.emit("ASSIGN", arg1=val, result=stmt.var_name)
        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                self._gen_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            cond_val = self._gen_expr(stmt.condition)
            lbl_else = self.new_label("L_else")
            lbl_end = self.new_label("L_ifend")

            if stmt.else_branch:
                self.emit("IF_FALSE", arg1=cond_val, result=lbl_else)
                self._gen_stmt(stmt.then_branch)
                self.emit("GOTO", result=lbl_end)
                self.emit("LABEL", result=lbl_else)
                self._gen_stmt(stmt.else_branch)
                self.emit("LABEL", result=lbl_end)
            else:
                self.emit("IF_FALSE", arg1=cond_val, result=lbl_end)
                self._gen_stmt(stmt.then_branch)
                self.emit("LABEL", result=lbl_end)

        elif isinstance(stmt, WhileStmt):
            lbl_start = self.new_label("L_while_cond")
            lbl_end = self.new_label("L_while_end")

            self.emit("LABEL", result=lbl_start)
            cond_val = self._gen_expr(stmt.condition)
            self.emit("IF_FALSE", arg1=cond_val, result=lbl_end)
            self._gen_stmt(stmt.body)
            self.emit("GOTO", result=lbl_start)
            self.emit("LABEL", result=lbl_end)

        elif isinstance(stmt, ForStmt):
            lbl_cond = self.new_label("L_for_cond")
            lbl_step = self.new_label("L_for_step")
            lbl_end = self.new_label("L_for_end")

            if stmt.init:
                self._gen_stmt(stmt.init)

            self.emit("LABEL", result=lbl_cond)
            if stmt.condition:
                cond_val = self._gen_expr(stmt.condition)
                self.emit("IF_FALSE", arg1=cond_val, result=lbl_end)

            self._gen_stmt(stmt.body)

            self.emit("LABEL", result=lbl_step)
            if stmt.update:
                self._gen_expr(stmt.update)
            self.emit("GOTO", result=lbl_cond)

            self.emit("LABEL", result=lbl_end)

        elif isinstance(stmt, ReturnStmt):
            ret_val = self._gen_expr(stmt.expr) if stmt.expr else None
            self.emit("RETURN", arg1=ret_val)

    def _gen_expr(self, expr: ASTNode) -> str:
        if isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, AssignExpr):
            rhs = self._gen_expr(expr.value)
            self.emit("ASSIGN", arg1=rhs, result=expr.target)
            return expr.target
        elif isinstance(expr, BinaryOp):
            l = self._gen_expr(expr.left)
            r = self._gen_expr(expr.right)
            t = self.new_temp()
            self.emit(expr.op, arg1=l, arg2=r, result=t)
            return t
        elif isinstance(expr, UnaryOp):
            v = self._gen_expr(expr.operand)
            t = self.new_temp()
            op_code = "NEG" if expr.op == "-" else ("NOT" if expr.op == "!" else "POS")
            self.emit(op_code, arg1=v, result=t)
            return t
        elif isinstance(expr, FuncCall):
            arg_temps = [self._gen_expr(a) for a in expr.args]
            for a in arg_temps:
                self.emit("PARAM", arg1=a)
            t = self.new_temp()
            self.emit("CALL", arg1=expr.name, arg2=str(len(arg_temps)), result=t)
            return t
        return "0"
