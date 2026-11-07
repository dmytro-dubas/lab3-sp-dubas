
import unittest
from py_compiler.parser import CParser
from py_compiler.semantics import SemanticAnalyzer, ASTInterpreter
from py_compiler.ast_nodes import Literal

class TestSemantics(unittest.TestCase):
    def setUp(self):
        self.parser = CParser()
        self.analyzer = SemanticAnalyzer()
        self.interpreter = ASTInterpreter()

    def test_constant_folding_arithmetic(self):
        code = "int test() { int x = 2 + 3 * 4; return x; }"
        ast = self.parser.parse(code)
        folded = ast.fold()
        decl = folded.declarations[0].body.statements[0]
        self.assertIsInstance(decl.init_expr, Literal)
        self.assertEqual(decl.init_expr.value, 14)

    def test_constant_folding_complex(self):
        code = "int test() { int x = (10 - 4) * (8 / 2) + (15 % 4); return x; }"
        ast = self.parser.parse(code)
        folded = ast.fold()
        decl = folded.declarations[0].body.statements[0]
        self.assertIsInstance(decl.init_expr, Literal)
        self.assertEqual(decl.init_expr.value, 27)

    def test_undeclared_variable_error(self):
        code = "int test() { return undefined_var + 10; }"
        ast = self.parser.parse(code)
        diags = self.analyzer.analyze(ast)
        errors = [d for d in diags if d.severity == "ERROR"]
        self.assertTrue(any("undefined_var" in d.message for d in errors))

    def test_duplicate_declaration_error(self):
        code = "int test() { int a = 5; int a = 10; return a; }"
        ast = self.parser.parse(code)
        diags = self.analyzer.analyze(ast)
        errors = [d for d in diags if d.severity == "ERROR"]
        self.assertTrue(any("Повторне оголошення" in d.message for d in errors))

    def test_ast_evaluation_recursion(self):
        code = """
        int fact(int n) {
            if (n <= 1) return 1;
            return n * fact(n - 1);
        }
        int main() {
            return fact(5);
        }
        """
        ast = self.parser.parse(code)
        res = self.interpreter.execute(ast)
        self.assertEqual(res, 120)

    def test_short_circuit_evaluation(self):
        code = "int main() { int x = 0; if (0 && (1 / 0)) x = 1; return x; }"
        ast = self.parser.parse(code)
        res = self.interpreter.execute(ast)
        self.assertEqual(res, 0)

        code2 = "int main() { int x = 0; if (1 || (1 / 0)) x = 1; return x; }"
        ast2 = self.parser.parse(code2)
        res2 = self.interpreter.execute(ast2)
        self.assertEqual(res2, 1)

    def test_zero_division_handling(self):
        code = "int main() { return 10 / 0; }"
        ast = self.parser.parse(code)
        with self.assertRaises(ZeroDivisionError):
            self.interpreter.execute(ast)

if __name__ == "__main__":
    unittest.main()
