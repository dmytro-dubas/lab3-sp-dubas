
import unittest
from py_compiler.parser import CParser

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.parser = CParser()

    def test_keywords_and_identifiers(self):
        code = "int main() { int count_1 = 42; return count_1; }"
        ast = self.parser.parse(code)
        self.assertEqual(len(ast.declarations), 1)
        func = ast.declarations[0]
        self.assertEqual(func.name, "main")
        self.assertEqual(func.return_type, "int")

    def test_numeric_literals(self):
        code = "void test() { int a = 123; float b = 3.1415; }"
        ast = self.parser.parse(code)
        body = ast.declarations[0].body.statements
        self.assertEqual(body[0].init_expr.value, 123)
        self.assertEqual(body[0].init_expr.val_type, "int")
        self.assertAlmostEqual(body[1].init_expr.value, 3.1415, places=4)
        self.assertEqual(body[1].init_expr.val_type, "float")

    def test_comments_skipping(self):
        code = """
        // Однорядковий коментар
        /* Багаторядковий
           коментар C */
        int test_comment() {
            int x = 10; // ініціалізація
            /* ще коментар */
            return x;
        }
        """
        ast = self.parser.parse(code)
        self.assertEqual(len(ast.declarations), 1)
        self.assertEqual(ast.declarations[0].name, "test_comment")

if __name__ == "__main__":
    unittest.main()
