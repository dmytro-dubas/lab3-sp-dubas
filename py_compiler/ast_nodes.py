
from dataclasses import dataclass, field
from typing import List, Optional, Any, Union

@dataclass
class ASTNode:
    line: int = 1
    col: int = 1

    def to_dict(self) -> dict:
        raise NotImplementedError

    def pretty(self, indent: int = 0) -> str:
        raise NotImplementedError

    def fold(self) -> 'ASTNode':
        return self

@dataclass
class Literal(ASTNode):
    value: Union[int, float, str] = 0
    val_type: str = "int"

    def to_dict(self) -> dict:
        return {
            "name": f"Literal: {self.value}",
            "type": "Literal",
            "val": self.value,
            "category": "literal",
            "dataType": self.val_type,
            "children": []
        }

    def pretty(self, indent: int = 0) -> str:
        return "  " * indent + f"Literal({self.value}: {self.val_type})\n"

    def fold(self) -> 'Literal':
        return self


@dataclass
class Identifier(ASTNode):
    name: str = ""

    def to_dict(self) -> dict:
        return {
            "name": f"Id: {self.name}",
            "type": "Identifier",
            "val": self.name,
            "category": "identifier",
            "children": []
        }

    def pretty(self, indent: int = 0) -> str:
        return "  " * indent + f"Identifier({self.name})\n"

    def fold(self) -> 'Identifier':
        return self


@dataclass
class BinaryOp(ASTNode):
    op: str = "+"
    left: ASTNode = None
    right: ASTNode = None

    def to_dict(self) -> dict:
        return {
            "name": f"BinaryOp: {self.op}",
            "type": "BinaryOp",
            "op": self.op,
            "category": "operator",
            "children": [
                self.left.to_dict() if self.left else {},
                self.right.to_dict() if self.right else {}
            ]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"BinaryOp({self.op})\n"
        if self.left:
            res += self.left.pretty(indent + 1)
        if self.right:
            res += self.right.pretty(indent + 1)
        return res

    def fold(self) -> ASTNode:
        f_left = self.left.fold() if self.left else None
        f_right = self.right.fold() if self.right else None

        if isinstance(f_left, Literal) and isinstance(f_right, Literal):
            v1, v2 = f_left.value, f_right.value
            res_val = None
            res_type = "float" if ("float" in (f_left.val_type, f_right.val_type) or isinstance(v1, float) or isinstance(v2, float)) else "int"

            try:
                if self.op == "+":
                    res_val = v1 + v2
                elif self.op == "-":
                    res_val = v1 - v2
                elif self.op == "*":
                    res_val = v1 * v2
                elif self.op == "/":
                    if v2 == 0:
                        return BinaryOp(op=self.op, left=f_left, right=f_right, line=self.line, col=self.col)
                    res_val = v1 / v2 if res_type == "float" else int(v1 // v2)
                elif self.op == "%":
                    if v2 == 0:
                        return BinaryOp(op=self.op, left=f_left, right=f_right, line=self.line, col=self.col)
                    res_val = int(v1 % v2)
                elif self.op == "==":
                    res_val = 1 if v1 == v2 else 0
                    res_type = "int"
                elif self.op == "!=":
                    res_val = 1 if v1 != v2 else 0
                    res_type = "int"
                elif self.op == "<":
                    res_val = 1 if v1 < v2 else 0
                    res_type = "int"
                elif self.op == "<=":
                    res_val = 1 if v1 <= v2 else 0
                    res_type = "int"
                elif self.op == ">":
                    res_val = 1 if v1 > v2 else 0
                    res_type = "int"
                elif self.op == ">=":
                    res_val = 1 if v1 >= v2 else 0
                    res_type = "int"
                elif self.op == "&&":
                    res_val = 1 if (v1 and v2) else 0
                    res_type = "int"
                elif self.op == "||":
                    res_val = 1 if (v1 or v2) else 0
                    res_type = "int"

                if res_val is not None:
                    if res_type == "int":
                        res_val = int(res_val)
                    else:
                        res_val = float(res_val)
                    return Literal(value=res_val, val_type=res_type, line=self.line, col=self.col)
            except Exception:
                pass

        return BinaryOp(op=self.op, left=f_left, right=f_right, line=self.line, col=self.col)


@dataclass
class UnaryOp(ASTNode):
    op: str = "-"
    operand: ASTNode = None

    def to_dict(self) -> dict:
        return {
            "name": f"UnaryOp: {self.op}",
            "type": "UnaryOp",
            "op": self.op,
            "category": "operator",
            "children": [self.operand.to_dict() if self.operand else {}]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"UnaryOp({self.op})\n"
        if self.operand:
            res += self.operand.pretty(indent + 1)
        return res

    def fold(self) -> ASTNode:
        f_op = self.operand.fold() if self.operand else None
        if isinstance(f_op, Literal):
            v = f_op.value
            if self.op == "-":
                return Literal(value=-v, val_type=f_op.val_type, line=self.line, col=self.col)
            elif self.op == "+":
                return Literal(value=+v, val_type=f_op.val_type, line=self.line, col=self.col)
            elif self.op == "!":
                return Literal(value=0 if v else 1, val_type="int", line=self.line, col=self.col)
        return UnaryOp(op=self.op, operand=f_op, line=self.line, col=self.col)


@dataclass
class AssignExpr(ASTNode):
    target: str = ""
    value: ASTNode = None

    def to_dict(self) -> dict:
        return {
            "name": f"Assign: {self.target} =",
            "type": "AssignExpr",
            "target": self.target,
            "category": "statement",
            "children": [self.value.to_dict() if self.value else {}]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"AssignExpr({self.target} = )\n"
        if self.value:
            res += self.value.pretty(indent + 1)
        return res

    def fold(self) -> 'AssignExpr':
        return AssignExpr(target=self.target, value=self.value.fold() if self.value else None, line=self.line, col=self.col)


@dataclass
class FuncCall(ASTNode):
    name: str = ""
    args: List[ASTNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": f"Call: {self.name}()",
            "type": "FuncCall",
            "funcName": self.name,
            "category": "function",
            "children": [arg.to_dict() for arg in self.args]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"FuncCall({self.name})\n"
        for arg in self.args:
            res += arg.pretty(indent + 1)
        return res

    def fold(self) -> 'FuncCall':
        return FuncCall(name=self.name, args=[arg.fold() for arg in self.args], line=self.line, col=self.col)

@dataclass
class CompoundStmt(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": "Block { ... }",
            "type": "CompoundStmt",
            "category": "structure",
            "children": [stmt.to_dict() for stmt in self.statements]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "CompoundStmt {\n"
        for stmt in self.statements:
            res += stmt.pretty(indent + 1)
        res += "  " * indent + "}\n"
        return res

    def fold(self) -> 'CompoundStmt':
        return CompoundStmt(statements=[s.fold() for s in self.statements], line=self.line, col=self.col)


@dataclass
class VarDecl(ASTNode):
    type_name: str = "int"
    var_name: str = ""
    init_expr: Optional[ASTNode] = None

    def to_dict(self) -> dict:
        children = []
        if self.init_expr:
            children.append(self.init_expr.to_dict())
        return {
            "name": f"VarDecl: {self.type_name} {self.var_name}",
            "type": "VarDecl",
            "varType": self.type_name,
            "varName": self.var_name,
            "category": "declaration",
            "children": children
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"VarDecl({self.type_name} {self.var_name}"
        if self.init_expr:
            res += " =\n" + self.init_expr.pretty(indent + 1) + ("  " * indent + ")\n")
        else:
            res += ")\n"
        return res

    def fold(self) -> 'VarDecl':
        return VarDecl(
            type_name=self.type_name,
            var_name=self.var_name,
            init_expr=self.init_expr.fold() if self.init_expr else None,
            line=self.line,
            col=self.col
        )


@dataclass
class ExprStmt(ASTNode):
    expr: Optional[ASTNode] = None

    def to_dict(self) -> dict:
        return {
            "name": "ExprStmt",
            "type": "ExprStmt",
            "category": "statement",
            "children": [self.expr.to_dict()] if self.expr else []
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "ExprStmt:\n"
        if self.expr:
            res += self.expr.pretty(indent + 1)
        return res

    def fold(self) -> 'ExprStmt':
        return ExprStmt(expr=self.expr.fold() if self.expr else None, line=self.line, col=self.col)


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode = None
    then_branch: ASTNode = None
    else_branch: Optional[ASTNode] = None

    def to_dict(self) -> dict:
        children = [
            {"name": "Condition", "type": "Condition", "category": "control", "children": [self.condition.to_dict()] if self.condition else []},
            {"name": "Then", "type": "ThenBranch", "category": "control", "children": [self.then_branch.to_dict()] if self.then_branch else []}
        ]
        if self.else_branch:
            children.append({
                "name": "Else", "type": "ElseBranch", "category": "control", "children": [self.else_branch.to_dict()]
            })
        return {
            "name": "IfStmt",
            "type": "IfStmt",
            "category": "control",
            "children": children
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "IfStmt:\n"
        res += "  " * (indent + 1) + "[Condition]:\n" + (self.condition.pretty(indent + 2) if self.condition else "")
        res += "  " * (indent + 1) + "[Then]:\n" + (self.then_branch.pretty(indent + 2) if self.then_branch else "")
        if self.else_branch:
            res += "  " * (indent + 1) + "[Else]:\n" + self.else_branch.pretty(indent + 2)
        return res

    def fold(self) -> ASTNode:
        f_cond = self.condition.fold() if self.condition else None
        f_then = self.then_branch.fold() if self.then_branch else None
        f_else = self.else_branch.fold() if self.else_branch else None

        if isinstance(f_cond, Literal):
            if f_cond.value:
                return f_then
            else:
                return f_else if f_else else CompoundStmt(statements=[], line=self.line, col=self.col)

        return IfStmt(condition=f_cond, then_branch=f_then, else_branch=f_else, line=self.line, col=self.col)


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode = None
    body: ASTNode = None

    def to_dict(self) -> dict:
        return {
            "name": "WhileLoop",
            "type": "WhileStmt",
            "category": "control",
            "children": [
                {"name": "Condition", "type": "Condition", "category": "control", "children": [self.condition.to_dict()] if self.condition else []},
                {"name": "Body", "type": "LoopBody", "category": "control", "children": [self.body.to_dict()] if self.body else []}
            ]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "WhileStmt:\n"
        res += "  " * (indent + 1) + "[Condition]:\n" + (self.condition.pretty(indent + 2) if self.condition else "")
        res += "  " * (indent + 1) + "[Body]:\n" + (self.body.pretty(indent + 2) if self.body else "")
        return res

    def fold(self) -> 'WhileStmt':
        return WhileStmt(
            condition=self.condition.fold() if self.condition else None,
            body=self.body.fold() if self.body else None,
            line=self.line,
            col=self.col
        )


@dataclass
class ForStmt(ASTNode):
    init: Optional[ASTNode] = None
    condition: Optional[ASTNode] = None
    update: Optional[ASTNode] = None
    body: ASTNode = None

    def to_dict(self) -> dict:
        children = []
        if self.init:
            children.append({"name": "ForInit", "type": "ForInit", "category": "control", "children": [self.init.to_dict()]})
        if self.condition:
            children.append({"name": "ForCond", "type": "ForCond", "category": "control", "children": [self.condition.to_dict()]})
        if self.update:
            children.append({"name": "ForStep", "type": "ForStep", "category": "control", "children": [self.update.to_dict()]})
        if self.body:
            children.append({"name": "ForBody", "type": "ForBody", "category": "control", "children": [self.body.to_dict()]})
        return {
            "name": "ForLoop",
            "type": "ForStmt",
            "category": "control",
            "children": children
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "ForStmt:\n"
        if self.init:
            res += "  " * (indent + 1) + "[Init]:\n" + self.init.pretty(indent + 2)
        if self.condition:
            res += "  " * (indent + 1) + "[Cond]:\n" + self.condition.pretty(indent + 2)
        if self.update:
            res += "  " * (indent + 1) + "[Step]:\n" + self.update.pretty(indent + 2)
        if self.body:
            res += "  " * (indent + 1) + "[Body]:\n" + self.body.pretty(indent + 2)
        return res

    def fold(self) -> 'ForStmt':
        return ForStmt(
            init=self.init.fold() if self.init else None,
            condition=self.condition.fold() if self.condition else None,
            update=self.update.fold() if self.update else None,
            body=self.body.fold() if self.body else None,
            line=self.line,
            col=self.col
        )


@dataclass
class ReturnStmt(ASTNode):
    expr: Optional[ASTNode] = None

    def to_dict(self) -> dict:
        return {
            "name": "Return",
            "type": "ReturnStmt",
            "category": "statement",
            "children": [self.expr.to_dict()] if self.expr else []
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "ReturnStmt\n"
        if self.expr:
            res += self.expr.pretty(indent + 1)
        return res

    def fold(self) -> 'ReturnStmt':
        return ReturnStmt(expr=self.expr.fold() if self.expr else None, line=self.line, col=self.col)

@dataclass
class Param(ASTNode):
    type_name: str = "int"
    name: str = ""

    def to_dict(self) -> dict:
        return {
            "name": f"Param: {self.type_name} {self.name}",
            "type": "Param",
            "paramType": self.type_name,
            "paramName": self.name,
            "category": "declaration",
            "children": []
        }

    def pretty(self, indent: int = 0) -> str:
        return "  " * indent + f"Param({self.type_name} {self.name})\n"


@dataclass
class FunctionDef(ASTNode):
    return_type: str = "int"
    name: str = ""
    params: List[Param] = field(default_factory=list)
    body: Optional[CompoundStmt] = None

    def to_dict(self) -> dict:
        param_nodes = [p.to_dict() for p in self.params]
        body_node = self.body.to_dict() if self.body else {}
        return {
            "name": f"Function: {self.return_type} {self.name}()",
            "type": "FunctionDef",
            "returnType": self.return_type,
            "funcName": self.name,
            "category": "function",
            "children": [
                {"name": f"Params ({len(self.params)})", "type": "ParamList", "category": "declaration", "children": param_nodes},
                body_node
            ]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + f"FunctionDef({self.return_type} {self.name}(\n"
        for p in self.params:
            res += p.pretty(indent + 1)
        res += "  " * indent + ")):\n"
        if self.body:
            res += self.body.pretty(indent + 1)
        return res

    def fold(self) -> 'FunctionDef':
        return FunctionDef(
            return_type=self.return_type,
            name=self.name,
            params=self.params,
            body=self.body.fold() if self.body else None,
            line=self.line,
            col=self.col
        )


@dataclass
class Program(ASTNode):
    declarations: List[Union[FunctionDef, VarDecl]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": "TranslationUnit (AST Root)",
            "type": "Program",
            "category": "root",
            "children": [decl.to_dict() for decl in self.declarations]
        }

    def pretty(self, indent: int = 0) -> str:
        res = "  " * indent + "Program (AST Root):\n"
        for decl in self.declarations:
            res += decl.pretty(indent + 1)
        return res

    def fold(self) -> 'Program':
        return Program(declarations=[d.fold() for d in self.declarations], line=self.line, col=self.col)
