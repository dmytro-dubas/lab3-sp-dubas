
from typing import List, Optional
from .ast_nodes import (
    ASTNode, Program, FunctionDef, Param, VarDecl, CompoundStmt,
    ExprStmt, IfStmt, WhileStmt, ForStmt, ReturnStmt,
    AssignExpr, BinaryOp, UnaryOp, FuncCall, Identifier, Literal
)

class TargetTranslator:

    def __init__(self):
        self.global_vars: List[str] = []

    def _is_float_expr(self, node: Optional[ASTNode]) -> bool:
        if node is None:
            return False
        if isinstance(node, Literal) and (node.val_type == "float" or isinstance(node.value, float)):
            return True
        if isinstance(node, BinaryOp):
            return self._is_float_expr(node.left) or self._is_float_expr(node.right)
        if isinstance(node, UnaryOp):
            return self._is_float_expr(node.operand)
        return False

    def to_python(self, program: Program) -> str:
        self.global_vars = [decl.var_name for decl in program.declarations if isinstance(decl, VarDecl)]
        lines: List[str] = []

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                lines.append(self._py_func(decl))
            elif isinstance(decl, VarDecl):
                init = self._py_expr(decl.init_expr) if decl.init_expr else "0"
                lines.append(f"{decl.var_name} = {init}")

        lines.extend([
            "",
            "if __name__ == '__main__':",
            "    if 'main' in globals():",
            "        result = main()",
            "        print(f'Результат виконання трансляції main(): {result}')"
        ])
        return "\n".join(lines)

    def _py_func(self, func: FunctionDef, indent: int = 0) -> str:
        ind = "    " * indent
        params = ", ".join(p.name for p in func.params)
        lines = [f"{ind}def {func.name}({params}):"]
        if self.global_vars:
            lines.append(f"{ind}    global {', '.join(self.global_vars)}")
        body_lines = self._py_compound(func.body, indent + 1)
        if not body_lines:
            lines.append(f"{ind}    pass")
        else:
            lines.extend(body_lines)
        lines.append("")
        return "\n".join(lines)

    def _py_compound(self, block: Optional[CompoundStmt], indent: int) -> List[str]:
        if not block:
            return []
        ind = "    " * indent
        lines = []
        for stmt in block.statements:
            lines.extend(self._py_stmt(stmt, indent))
        return lines

    def _py_stmt(self, stmt: ASTNode, indent: int) -> List[str]:
        ind = "    " * indent
        if isinstance(stmt, CompoundStmt):
            return self._py_compound(stmt, indent)
        elif isinstance(stmt, VarDecl):
            val = self._py_expr(stmt.init_expr) if stmt.init_expr else "0"
            return [f"{ind}{stmt.var_name} = {val}"]
        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                return [f"{ind}{self._py_expr(stmt.expr)}"]
            return []
        elif isinstance(stmt, IfStmt):
            cond = self._py_expr(stmt.condition)
            lines = [f"{ind}if {cond}:"]
            then_b = self._py_stmt(stmt.then_branch, indent + 1)
            lines.extend(then_b if then_b else [f"{ind}    pass"])
            if stmt.else_branch:
                lines.append(f"{ind}else:")
                else_b = self._py_stmt(stmt.else_branch, indent + 1)
                lines.extend(else_b if else_b else [f"{ind}    pass"])
            return lines
        elif isinstance(stmt, WhileStmt):
            cond = self._py_expr(stmt.condition)
            lines = [f"{ind}while {cond}:"]
            body = self._py_stmt(stmt.body, indent + 1)
            lines.extend(body if body else [f"{ind}    pass"])
            return lines
        elif isinstance(stmt, ForStmt):
            lines = []
            if stmt.init:
                lines.extend(self._py_stmt(stmt.init, indent))
            cond = self._py_expr(stmt.condition) if stmt.condition else "True"
            lines.append(f"{ind}while {cond}:")
            body = self._py_stmt(stmt.body, indent + 1)
            lines.extend(body if body else [f"{ind}    pass"])
            if stmt.update:
                lines.append(f"{ind}    {self._py_expr(stmt.update)}")
            return lines
        elif isinstance(stmt, ReturnStmt):
            val = self._py_expr(stmt.expr) if stmt.expr else ""
            return [f"{ind}return {val}"]
        return []

    def _py_expr(self, expr: Optional[ASTNode]) -> str:
        if expr is None:
            return "0"
        if isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, AssignExpr):
            return f"{expr.target} = {self._py_expr(expr.value)}"
        elif isinstance(expr, BinaryOp):
            l = self._py_expr(expr.left)
            r = self._py_expr(expr.right)
            op = expr.op
            if op == "&&": op = "and"
            elif op == "||": op = "or"
            elif op == "/":
                if self._is_float_expr(expr.left) or self._is_float_expr(expr.right):
                    return f"({l} / {r})"
                return f"int({l} / {r})"
            return f"({l} {op} {r})"
        elif isinstance(expr, UnaryOp):
            v = self._py_expr(expr.operand)
            if expr.op == "!":
                return f"(not {v})"
            return f"({expr.op}{v})"
        elif isinstance(expr, FuncCall):
            args = ", ".join(self._py_expr(a) for a in expr.args)
            return f"{expr.name}({args})"
        return "0"

    def to_javascript(self, program: Program) -> str:
        lines: List[str] = []

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                lines.append(self._js_func(decl))
            elif isinstance(decl, VarDecl):
                init = self._js_expr(decl.init_expr) if decl.init_expr else "0"
                lines.append(f"let {decl.var_name} = {init};")

        lines.extend([
            "",
            "if (typeof main === 'function') {",
            "    console.log('Результат виконання трансляції main():', main());",
            "}"
        ])
        return "\n".join(lines)

    def _js_func(self, func: FunctionDef, indent: int = 0) -> str:
        ind = "  " * indent
        params = ", ".join(p.name for p in func.params)
        lines = [f"{ind}function {func.name}({params}) {{"]
        if func.body:
            for s in func.body.statements:
                lines.extend(self._js_stmt(s, indent + 1))
        lines.append(f"{ind}}}")
        return "\n".join(lines)

    def _js_stmt(self, stmt: ASTNode, indent: int) -> List[str]:
        ind = "  " * indent
        if isinstance(stmt, CompoundStmt):
            lines = [f"{ind}{{"]
            for s in stmt.statements:
                lines.extend(self._js_stmt(s, indent + 1))
            lines.append(f"{ind}}}")
            return lines
        elif isinstance(stmt, VarDecl):
            val = self._js_expr(stmt.init_expr) if stmt.init_expr else "0"
            return [f"{ind}let {stmt.var_name} = {val};"]
        elif isinstance(stmt, ExprStmt):
            if stmt.expr:
                return [f"{ind}{self._js_expr(stmt.expr)};"]
            return []
        elif isinstance(stmt, IfStmt):
            cond = self._js_expr(stmt.condition)
            lines = [f"{ind}if ({cond}) {{"]
            lines.extend(self._js_stmt(stmt.then_branch, indent + 1))
            if stmt.else_branch:
                lines.append(f"{ind}}} else {{")
                lines.extend(self._js_stmt(stmt.else_branch, indent + 1))
            lines.append(f"{ind}}}")
            return lines
        elif isinstance(stmt, WhileStmt):
            cond = self._js_expr(stmt.condition)
            lines = [f"{ind}while ({cond}) {{"]
            lines.extend(self._js_stmt(stmt.body, indent + 1))
            lines.append(f"{ind}}}")
            return lines
        elif isinstance(stmt, ForStmt):
            init_s = ""
            if stmt.init:
                if isinstance(stmt.init, VarDecl):
                    init_s = f"let {stmt.init.var_name} = {self._js_expr(stmt.init.init_expr)}"
                elif isinstance(stmt.init, ExprStmt):
                    init_s = self._js_expr(stmt.init.expr) if stmt.init.expr else ""
                elif isinstance(stmt.init, CompoundStmt) and stmt.init.statements:
                    inits = []
                    for s in stmt.init.statements:
                        if isinstance(s, VarDecl):
                            inits.append(f"let {s.var_name} = {self._js_expr(s.init_expr)}")
                        elif isinstance(s, ExprStmt) and s.expr:
                            inits.append(self._js_expr(s.expr))
                    init_s = ", ".join(inits)
            cond_s = self._js_expr(stmt.condition) if stmt.condition else ""
            step_s = self._js_expr(stmt.update) if stmt.update else ""
            lines = [f"{ind}for ({init_s}; {cond_s}; {step_s}) {{"]
            lines.extend(self._js_stmt(stmt.body, indent + 1))
            lines.append(f"{ind}}}")
            return lines
        elif isinstance(stmt, ReturnStmt):
            val = self._js_expr(stmt.expr) if stmt.expr else ""
            return [f"{ind}return {val};"]
        return []

    def _js_expr(self, expr: Optional[ASTNode]) -> str:
        if expr is None:
            return "0"
        if isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, AssignExpr):
            return f"{expr.target} = {self._js_expr(expr.value)}"
        elif isinstance(expr, BinaryOp):
            l = self._js_expr(expr.left)
            r = self._js_expr(expr.right)
            op = expr.op
            if op == "/":
                if self._is_float_expr(expr.left) or self._is_float_expr(expr.right):
                    return f"({l} / {r})"
                return f"Math.trunc({l} / {r})"
            return f"({l} {op} {r})"
        elif isinstance(expr, UnaryOp):
            v = self._js_expr(expr.operand)
            return f"({expr.op}{v})"
        elif isinstance(expr, FuncCall):
            args = ", ".join(self._js_expr(a) for a in expr.args)
            return f"{expr.name}({args})"
        return "0"
