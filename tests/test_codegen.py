
import unittest
from py_compiler.parser import CParser
from py_compiler.ir_generator import IRGenerator
from py_compiler.x86_codegen import X86CodeGenerator
from py_compiler.target_translator import TargetTranslator

class TestCodegen(unittest.TestCase):
    def setUp(self):
        self.parser = CParser()
        self.ir_gen = IRGenerator()
        self.x86_gen = X86CodeGenerator()
        self.translator = TargetTranslator()

    def test_3ac_emission(self):
        code = "int calc() { int a = 5; int b = 10; return a + b * 2; }"
        ast = self.parser.parse(code)
        tac = self.ir_gen.generate(ast)
        tac_str = self.ir_gen.get_listing()

        self.assertIn("a = 5", tac_str)
        self.assertIn("b = 10", tac_str)
        self.assertIn("* 2", tac_str)
        self.assertIn("return", tac_str)

    def test_x86_assembly_structure(self):
        code = "int main() { return 42; }"
        ast = self.parser.parse(code)
        tac = self.ir_gen.generate(ast)
        asm = self.x86_gen.generate(tac)

        self.assertIn(".intel_syntax noprefix", asm)
        self.assertIn(".globl main", asm)
        self.assertIn("push rbp", asm)
        self.assertIn("mov rbp, rsp", asm)
        self.assertIn("leave", asm)
        self.assertIn("ret", asm)

    def test_python_translation_execution(self):
        code = """
        int sum_sq(int n) {
            int s = 0;
            for (int i = 1; i <= n; i = i + 1) {
                s = s + i * i;
            }
            return s;
        }
        int main() {
            return sum_sq(4); // 1 + 4 + 9 + 16 = 30
        }
        """
        ast = self.parser.parse(code).fold()
        py_code = self.translator.to_python(ast)
        
        env = {}
        exec(py_code, env)
        self.assertIn("main", env)
        res = env["main"]()
        self.assertEqual(res, 30)

    def test_js_translation_syntax(self):
        code = "int test(int a) { if (a > 0) return a; else return 0; }"
        ast = self.parser.parse(code)
        js_code = self.translator.to_javascript(ast)

        self.assertIn("function test(a)", js_code)
        self.assertIn("if ((a > 0))", js_code)
        self.assertIn("return a;", js_code)

    def test_float_literal_x86_codegen(self):
        code = "float avg() { float x = 10.0; return x / 2.0; }"
        ast = self.parser.parse(code)
        tac = self.ir_gen.generate(ast)
        asm = self.x86_gen.generate(tac)
        self.assertIn("mov ebx, 2", asm)
        self.assertNotIn("DWORD PTR [rbp - ", [line for line in asm.split("\n") if "2.0" in line])

    def test_for_loop_with_expr_init_js_translation(self):
        code = "int main() { int i; for (i = 0; i < 10; i = i + 1) {} return i; }"
        ast = self.parser.parse(code)
        js_code = self.translator.to_javascript(ast)
        self.assertIn("for (i = 0; (i < 10); i = (i + 1))", js_code)

    def test_float_division_preservation(self):
        code = "float div_test() { float a = 5.0; return a / 2.0; }"
        ast = self.parser.parse(code)
        py_code = self.translator.to_python(ast)
        js_code = self.translator.to_javascript(ast)
        self.assertIn("/ 2.0", py_code)
        self.assertNotIn("// 2.0", py_code)
        self.assertIn("(a / 2.0)", js_code)
        self.assertNotIn("Math.trunc(a / 2.0)", js_code)

if __name__ == "__main__":
    unittest.main()
