
from typing import List, Any
from lark import Lark, Transformer, v_args
from .grammar import C_GRAMMAR
from .ast_nodes import (
    ASTNode, Program, FunctionDef, Param, VarDecl, CompoundStmt,
    ExprStmt, IfStmt, WhileStmt, ForStmt, ReturnStmt,
    AssignExpr, BinaryOp, UnaryOp, FuncCall, Identifier, Literal
)

class _ForCondWrapper:
    def __init__(self, expr: ASTNode):
        self.expr = expr


class ASTTransformer(Transformer):

    def empty_param_list(self, _) -> List[Param]:
        return []

    def translation_unit(self, items) -> Program:
        flat_decls = []
        for item in items:
            if isinstance(item, list):
                flat_decls.extend(item)
            elif item is not None:
                flat_decls.append(item)
        return Program(declarations=flat_decls)

    def function_def(self, items) -> FunctionDef:
        if len(items) == 4:
            ret_type, name, params, body = items
            param_list = params if params is not None else []
        else:
            ret_type, name, body = items
            param_list = []
        return FunctionDef(
            return_type=str(ret_type),
            name=str(name),
            params=param_list,
            body=body
        )

    def type_int(self, _) -> str:
        return "int"

    def type_float(self, _) -> str:
        return "float"

    def type_void(self, _) -> str:
        return "void"

    def param_decl(self, items) -> Param:
        type_spec, name = items
        return Param(type_name=str(type_spec), name=str(name))

    def param_list(self, items) -> List[Param]:
        return list(items)

    def var_decl(self, items) -> List[VarDecl]:
        type_name, declarators = items
        result = []
        for decl in declarators:
            var_name, init_val = decl
            result.append(VarDecl(
                type_name=str(type_name),
                var_name=str(var_name),
                init_expr=init_val
            ))
        return result

    def init_declarator_list(self, items) -> List[tuple]:
        return list(items)

    def init_declarator(self, items) -> tuple:
        name = items[0]
        init_expr = items[1] if len(items) > 1 else None
        return (str(name), init_expr)

    def compound_stmt(self, items) -> CompoundStmt:
        stmts = []
        for item in items:
            if isinstance(item, list):
                stmts.extend(item)
            elif item is not None:
                stmts.append(item)
        return CompoundStmt(statements=stmts)

    def expr_stmt(self, items) -> ExprStmt:
        expr = items[0] if items and items[0] is not None else None
        return ExprStmt(expr=expr)

    def if_else_stmt(self, items) -> IfStmt:
        cond, then_br, else_br = items
        return IfStmt(condition=cond, then_branch=then_br, else_branch=else_br)

    def if_single_stmt(self, items) -> IfStmt:
        cond, then_br = items
        return IfStmt(condition=cond, then_branch=then_br, else_branch=None)

    def while_stmt(self, items) -> WhileStmt:
        cond, body = items
        return WhileStmt(condition=cond, body=body)

    def for_stmt(self, items) -> ForStmt:
        init_part = items[0]
        body = items[-1]
        cond = None
        update = None
        for mid in items[1:-1]:
            if isinstance(mid, _ForCondWrapper):
                cond = mid.expr
            else:
                update = mid

        init_node = None
        if init_part is not None:
            if isinstance(init_part, list):
                init_node = CompoundStmt(statements=init_part)
            else:
                init_node = init_part
        return ForStmt(init=init_node, condition=cond, update=update, body=body)

    def for_init_var(self, items) -> Any:
        return items[0]

    def for_init_expr(self, items) -> Any:
        return items[0]

    def for_cond(self, items) -> Any:
        return _ForCondWrapper(items[0])

    def return_stmt(self, items) -> ReturnStmt:
        expr = items[0] if items and items[0] is not None else None
        return ReturnStmt(expr=expr)

    def assign(self, items) -> AssignExpr:
        target, val = items
        return AssignExpr(target=str(target), value=val)

    def op_or(self, items) -> BinaryOp:
        return BinaryOp(op="||", left=items[0], right=items[1])

    def op_and(self, items) -> BinaryOp:
        return BinaryOp(op="&&", left=items[0], right=items[1])

    def op_eq(self, items) -> BinaryOp:
        return BinaryOp(op="==", left=items[0], right=items[1])

    def op_ne(self, items) -> BinaryOp:
        return BinaryOp(op="!=", left=items[0], right=items[1])

    def op_lt(self, items) -> BinaryOp:
        return BinaryOp(op="<", left=items[0], right=items[1])

    def op_le(self, items) -> BinaryOp:
        return BinaryOp(op="<=", left=items[0], right=items[1])

    def op_gt(self, items) -> BinaryOp:
        return BinaryOp(op=">", left=items[0], right=items[1])

    def op_ge(self, items) -> BinaryOp:
        return BinaryOp(op=">=", left=items[0], right=items[1])

    def op_add(self, items) -> BinaryOp:
        return BinaryOp(op="+", left=items[0], right=items[1])

    def op_sub(self, items) -> BinaryOp:
        return BinaryOp(op="-", left=items[0], right=items[1])

    def op_mul(self, items) -> BinaryOp:
        return BinaryOp(op="*", left=items[0], right=items[1])

    def op_div(self, items) -> BinaryOp:
        return BinaryOp(op="/", left=items[0], right=items[1])

    def op_mod(self, items) -> BinaryOp:
        return BinaryOp(op="%", left=items[0], right=items[1])

    def op_neg(self, items) -> UnaryOp:
        return UnaryOp(op="-", operand=items[0])

    def op_pos(self, items) -> UnaryOp:
        return UnaryOp(op="+", operand=items[0])

    def op_not(self, items) -> UnaryOp:
        return UnaryOp(op="!", operand=items[0])

    def func_call(self, items) -> FuncCall:
        name = str(items[0])
        args = items[1] if len(items) > 1 and items[1] is not None else []
        return FuncCall(name=name, args=args)

    def arg_list(self, items) -> List[ASTNode]:
        return list(items)

    def var(self, items) -> Identifier:
        return Identifier(name=str(items[0]))

    def number(self, items) -> Literal:
        val_str = str(items[0])
        if "." in val_str:
            return Literal(value=float(val_str), val_type="float")
        return Literal(value=int(val_str), val_type="int")


class CParser:

    def __init__(self):
        self._lark = Lark(
            C_GRAMMAR,
            parser='lalr',
            start='start',
            propagate_positions=True
        )
        self._transformer = ASTTransformer()

    def parse(self, source_code: str) -> Program:
        parse_tree = self._lark.parse(source_code)
        ast = self._transformer.transform(parse_tree)
        return ast
