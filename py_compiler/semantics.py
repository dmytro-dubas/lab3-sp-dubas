
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from .ast_nodes import (
    ASTNode, Program, FunctionDef, Param, VarDecl, CompoundStmt,
    ExprStmt, IfStmt, WhileStmt, ForStmt, ReturnStmt,
    AssignExpr, BinaryOp, UnaryOp, FuncCall, Identifier, Literal
)

@dataclass
class Symbol:
    name: str
    type_name: str
    kind: str
    params: List[str] = field(default_factory=list)
    scope_level: int = 0
    is_initialized: bool = False
    const_val: Any = None

class Scope:
    def __init__(self, parent: Optional['Scope'] = None, name: str = "local"):
        self.parent = parent
        self.name = name
        self.symbols: Dict[str, Symbol] = {}
        self.level = parent.level + 1 if parent else 0

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

@dataclass
class SemanticDiagnostic:
    severity: str
    message: str
    line: int = 1
    col: int = 1

class SemanticAnalyzer:

    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.diagnostics: List[SemanticDiagnostic] = []
        self.current_func: Optional[FunctionDef] = None

    def analyze(self, program: Program) -> List[SemanticDiagnostic]:
        self.diagnostics.clear()
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                sym = Symbol(
                    name=decl.name,
                    type_name=decl.return_type,
                    kind="func",
                    params=[p.type_name for p in decl.params],
                    scope_level=0
                )
                if not self.global_scope.define(sym):
                    self.diagnostics.append(SemanticDiagnostic(
                        "ERROR", f"Повторне оголошення функції '{decl.name}'", decl.line, decl.col
                    ))
            elif isinstance(decl, VarDecl):
                sym = Symbol(
                    name=decl.var_name,
                    type_name=decl.type_name,
                    kind="var",
                    scope_level=0,
                    is_initialized=(decl.init_expr is not None)
                )
                if not self.global_scope.define(sym):
                    self.diagnostics.append(SemanticDiagnostic(
                        "ERROR", f"Повторне оголошення глобальної змінної '{decl.var_name}'", decl.line, decl.col
                    ))

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                self._check_function(decl)
            elif isinstance(decl, VarDecl):
                if decl.init_expr:
                    self._check_expr(decl.init_expr)

        return self.diagnostics

    def _check_function(self, func: FunctionDef):
        self.current_func = func
        func_scope = Scope(parent=self.current_scope, name=f"func_{func.name}")
        self.current_scope = func_scope

        for p in func.params:
            sym = Symbol(name=p.name, type_name=p.type_name, kind="var", is_initialized=True)
            if not self.current_scope.define(sym):
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Повторне ім'я параметра '{p.name}' у функції '{func.name}'", p.line, p.col
                ))

        if func.body:
            self._check_compound(func.body, create_scope=False)

        self.current_scope = self.current_scope.parent
        self.current_func = None

    def _check_compound(self, block: CompoundStmt, create_scope: bool = True):
        if create_scope:
            block_scope = Scope(parent=self.current_scope, name="block")
            self.current_scope = block_scope

        for stmt in block.statements:
            self._check_stmt(stmt)

        if create_scope:
            self.current_scope = self.current_scope.parent

    def _check_stmt(self, stmt: ASTNode):
        if isinstance(stmt, CompoundStmt):
            self._check_compound(stmt, create_scope=True)
        elif isinstance(stmt, VarDecl):
            if stmt.init_expr:
                inferred = self._check_expr(stmt.init_expr)
                if stmt.type_name == "int" and inferred == "float":
                    self.diagnostics.append(SemanticDiagnostic(
                        "WARNING", f"Неявне звуження типу: присвоєння float змінній '{stmt.var_name}' типу int", stmt.line, stmt.col
                    ))
            sym = Symbol(
                name=stmt.var_name,
                type_name=stmt.type_name,
                kind="var",
                is_initialized=(stmt.init_expr is not None)
            )
            if not self.current_scope.define(sym):
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Повторне оголошення змінної '{stmt.var_name}' у тій самій області", stmt.line, stmt.col
                ))
        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                self._check_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self._check_expr(stmt.condition)
            self._check_stmt(stmt.then_branch)
            if stmt.else_branch:
                self._check_stmt(stmt.else_branch)
        elif isinstance(stmt, WhileStmt):
            self._check_expr(stmt.condition)
            self._check_stmt(stmt.body)
        elif isinstance(stmt, ForStmt):
            for_scope = Scope(parent=self.current_scope, name="for_scope")
            self.current_scope = for_scope
            if stmt.init:
                if isinstance(stmt.init, CompoundStmt):
                    for init_s in stmt.init.statements:
                        self._check_stmt(init_s)
                else:
                    self._check_stmt(stmt.init)
            if stmt.condition:
                self._check_expr(stmt.condition)
            if stmt.update:
                self._check_expr(stmt.update)
            if stmt.body:
                self._check_stmt(stmt.body)
            self.current_scope = self.current_scope.parent
        elif isinstance(stmt, ReturnStmt):
            if stmt.expr:
                inferred = self._check_expr(stmt.expr)
                if self.current_func and self.current_func.return_type == "void":
                    self.diagnostics.append(SemanticDiagnostic(
                        "ERROR", f"Повернення значення у функції '{self.current_func.name}' з типом void", stmt.line, stmt.col
                    ))

    def _check_expr(self, expr: ASTNode) -> str:
        if isinstance(expr, Literal):
            return expr.val_type
        elif isinstance(expr, Identifier):
            sym = self.current_scope.resolve(expr.name)
            if sym is None:
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Використання неоголошеної змінної '{expr.name}'", expr.line, expr.col
                ))
                return "int"
            return sym.type_name
        elif isinstance(expr, AssignExpr):
            sym = self.current_scope.resolve(expr.target)
            if sym is None:
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Присвоєння неоголошеній змінній '{expr.target}'", expr.line, expr.col
                ))
                rhs_type = self._check_expr(expr.value)
                return rhs_type
            rhs_type = self._check_expr(expr.value)
            if sym.type_name == "int" and rhs_type == "float":
                self.diagnostics.append(SemanticDiagnostic(
                    "WARNING", f"Неявне звуження типу при присвоєнні змінній '{expr.target}'", expr.line, expr.col
                ))
            return sym.type_name
        elif isinstance(expr, BinaryOp):
            t1 = self._check_expr(expr.left)
            t2 = self._check_expr(expr.right)
            if expr.op in ("==", "!=", "<", "<=", ">", ">=", "&&", "||"):
                return "int"
            if t1 == "float" or t2 == "float":
                return "float"
            return "int"
        elif isinstance(expr, UnaryOp):
            t = self._check_expr(expr.operand)
            if expr.op == "!":
                return "int"
            return t
        elif isinstance(expr, FuncCall):
            sym = self.global_scope.resolve(expr.name)
            if sym is None or sym.kind != "func":
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Виклик неоголошеної функції '{expr.name}'", expr.line, expr.col
                ))
                return "int"
            if len(expr.args) != len(sym.params):
                self.diagnostics.append(SemanticDiagnostic(
                    "ERROR", f"Функція '{expr.name}' очікує {len(sym.params)} аргументів, отримано {len(expr.args)}", expr.line, expr.col
                ))
            for arg in expr.args:
                self._check_expr(arg)
            return sym.type_name
        return "int"


class ASTInterpreter:

    def __init__(self):
        self.functions: Dict[str, FunctionDef] = {}
        self.globals: Dict[str, Any] = {}

    def execute(self, program: Program, entry_point: str = "main") -> Any:
        self.functions.clear()
        self.globals.clear()

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                self.functions[decl.name] = decl
            elif isinstance(decl, VarDecl):
                val = self._eval_expr(decl.init_expr, {}) if decl.init_expr else 0
                self.globals[decl.var_name] = val

        if entry_point not in self.functions:
            raise RuntimeError(f"Точка входу '{entry_point}' не знайдена у програмі!")

        return self._call_func(entry_point, [])

    def _call_func(self, name: str, args: List[Any]) -> Any:
        func = self.functions[name]
        env: Dict[str, Any] = {}

        for param, arg in zip(func.params, args):
            env[param.name] = arg

        try:
            self._exec_compound(func.body, env)
        except ReturnException as ret:
            return ret.value
        return 0

    def _exec_compound(self, block: CompoundStmt, env: Dict[str, Any]):
        for stmt in block.statements:
            self._exec_stmt(stmt, env)

    def _exec_stmt(self, stmt: ASTNode, env: Dict[str, Any]):
        if isinstance(stmt, CompoundStmt):
            self._exec_compound(stmt, env)
        elif isinstance(stmt, VarDecl):
            val = self._eval_expr(stmt.init_expr, env) if stmt.init_expr else 0
            env[stmt.var_name] = val
        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                self._eval_expr(stmt.expr, env)
        elif isinstance(stmt, IfStmt):
            c = self._eval_expr(stmt.condition, env)
            if c:
                self._exec_stmt(stmt.then_branch, env)
            elif stmt.else_branch:
                self._exec_stmt(stmt.else_branch, env)
        elif isinstance(stmt, WhileStmt):
            while self._eval_expr(stmt.condition, env):
                self._exec_stmt(stmt.body, env)
        elif isinstance(stmt, ForStmt):
            if stmt.init:
                self._exec_stmt(stmt.init, env)
            while True:
                if stmt.condition:
                    c = self._eval_expr(stmt.condition, env)
                    if not c:
                        break
                self._exec_stmt(stmt.body, env)
                if stmt.update:
                    self._eval_expr(stmt.update, env)
        elif isinstance(stmt, ReturnStmt):
            val = self._eval_expr(stmt.expr, env) if stmt.expr else None
            raise ReturnException(val)

    def _eval_expr(self, expr: ASTNode, env: Dict[str, Any]) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Identifier):
            if expr.name in env:
                return env[expr.name]
            if expr.name in self.globals:
                return self.globals[expr.name]
            raise RuntimeError(f"Неоголошена змінна '{expr.name}'")
        elif isinstance(expr, AssignExpr):
            val = self._eval_expr(expr.value, env)
            if expr.target in env:
                env[expr.target] = val
            else:
                self.globals[expr.target] = val
            return val
        elif isinstance(expr, BinaryOp):
            op = expr.op
            if op == "&&":
                l = self._eval_expr(expr.left, env)
                if not l:
                    return 0
                r = self._eval_expr(expr.right, env)
                return 1 if r else 0
            elif op == "||":
                l = self._eval_expr(expr.left, env)
                if l:
                    return 1
                r = self._eval_expr(expr.right, env)
                return 1 if r else 0

            l = self._eval_expr(expr.left, env)
            r = self._eval_expr(expr.right, env)
            if op == "+": return l + r
            if op == "-": return l - r
            if op == "*": return l * r
            if op == "/":
                if r == 0:
                    raise ZeroDivisionError(f"Ділення на нуль у виразі (рядок {expr.line})")
                return l / r if isinstance(l, float) or isinstance(r, float) else int(l / r)
            if op == "%":
                if r == 0:
                    raise ZeroDivisionError(f"Ділення на нуль за модулем (рядок {expr.line})")
                return l % r
            if op == "==": return 1 if l == r else 0
            if op == "!=": return 1 if l != r else 0
            if op == "<": return 1 if l < r else 0
            if op == "<=": return 1 if l <= r else 0
            if op == ">": return 1 if l > r else 0
            if op == ">=": return 1 if l >= r else 0
            raise NotImplementedError(f"Невідомий бінарний оператор {op}")
        elif isinstance(expr, UnaryOp):
            v = self._eval_expr(expr.operand, env)
            if expr.op == "-": return -v
            if expr.op == "+": return +v
            if expr.op == "!": return 0 if v else 1
            raise NotImplementedError(f"Невідомий унарний оператор {expr.op}")
        elif isinstance(expr, FuncCall):
            arg_vals = [self._eval_expr(a, env) for a in expr.args]
            return self._call_func(expr.name, arg_vals)
        return 0

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value
