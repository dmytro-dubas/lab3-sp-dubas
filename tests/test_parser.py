
import unittest
from py_compiler.parser import CParser
from py_compiler.ast_nodes import BinaryOp, Literal, IfStmt, WhileStmt, ForStmt

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = CParser()

    def test_arithmetic_precedence(self):
        code = "int test() { return 2 + 3 * 4; }"
        ast = self.parser.parse(code)
        ret_expr = ast.declarations[0].body.statements[0].expr

        self.assertIsInstance(ret_expr, BinaryOp)
        self.assertEqual(ret_expr.op, "+")
        self.assertIsInstance(ret_expr.left, Literal)
        self.assertEqual(ret_expr.left.value, 2)

        self.assertIsInstance(ret_expr.right, BinaryOp)
        self.assertEqual(ret_expr.right.op, "*")
        self.assertEqual(ret_expr.right.left.value, 3)
        self.assertEqual(ret_expr.right.right.value, 4)

    def test_parentheses_precedence(self):
        code = "int test() { return (2 + 3) * 4; }"
        ast = self.parser.parse(code)
        ret_expr = ast.declarations[0].body.statements[0].expr

        self.assertIsInstance(ret_expr, BinaryOp)
        self.assertEqual(ret_expr.op, "*")
        self.assertIsInstance(ret_expr.left, BinaryOp)
        self.assertEqual(ret_expr.left.op, "+")
        self.assertEqual(ret_expr.right.value, 4)

    def test_relational_and_logical_precedence(self):
        code = "int test() { return a > 5 && b <= 10 || c == 20; }"
        ast = self.parser.parse(code)
        ret_expr = ast.declarations[0].body.statements[0].expr
        self.assertEqual(ret_expr.op, "||")
        self.assertEqual(ret_expr.left.op, "&&")

    def test_if_else_structure(self):
        code = "void check(int x) { if (x > 0) return 1; else return 0; }"
        ast = self.parser.parse(code)
        stmt = ast.declarations[0].body.statements[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsNotNone(stmt.else_branch)

    def test_loops_structure(self):
        code = """
        void loop_test() {
            int i = 0;
            while (i < 10) { i = i + 1; }
            for (int j = 0; j < 5; j = j + 1) { i = i + j; }
        }
        """
        ast = self.parser.parse(code)
        stmts = ast.declarations[0].body.statements
        self.assertIsInstance(stmts[1], WhileStmt)
        self.assertIsInstance(stmts[2], ForStmt)

    def test_for_omitted_clauses(self):
        codes = [
            "void f() { for (;;); }",
            "void f() { for (; i < 10;); }",
            "void f() { for (;; i = i + 1); }",
            "void f() { for (int i = 0;;); }"
        ]
        for c in codes:
            ast = self.parser.parse(c)
            for_node = ast.declarations[0].body.statements[0]
            self.assertIsInstance(for_node, ForStmt)

    def test_void_parameter_function(self):
        code = "int test(void) { return 42; }"
        ast = self.parser.parse(code)
        func = ast.declarations[0]
        self.assertEqual(len(func.params), 0)

if __name__ == "__main__":
    unittest.main()
