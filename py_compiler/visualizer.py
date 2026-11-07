
import os
import json
import webbrowser
from typing import Optional
from .parser import CParser
from .semantics import SemanticAnalyzer, ASTInterpreter
from .ir_generator import IRGenerator
from .x86_codegen import X86CodeGenerator
from .target_translator import TargetTranslator
from .ast_nodes import Program

class ASTVisualizerService:

    def __init__(self, visualizer_dir: Optional[str] = None):
        if visualizer_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.visualizer_dir = os.path.join(base_dir, "visualizer")
        else:
            self.visualizer_dir = visualizer_dir

        self.parser = CParser()
        self.analyzer = SemanticAnalyzer()
        self.interpreter = ASTInterpreter()
        self.ir_gen = IRGenerator()
        self.x86_gen = X86CodeGenerator()
        self.translator = TargetTranslator()

    def compile_and_export(self, source_code: str, output_json_name: str = "ast_data.json") -> dict:
        ast = self.parser.parse(source_code)

        folded_ast = ast.fold()

        diags = self.analyzer.analyze(folded_ast)
        sem_lines = ["Семантичний аналіз:"]
        if not diags:
            sem_lines.append("Статус: успішно (0 помилок)")
        else:
            for d in diags:
                sem_lines.append(f"  [{d.severity}] рядок {d.line}: {d.message}")

        sem_lines.append("\nГлобальна таблиця символів:")
        for name, sym in self.analyzer.global_scope.symbols.items():
            sem_lines.append(f"  - {name}: {sym.type_name} ({sym.kind})")

        try:
            interp_res = self.interpreter.execute(folded_ast)
            sem_lines.append(f"\nОбчислення AST:\nРезультат виконання main(): {interp_res}")
        except Exception as e:
            sem_lines.append(f"\nОбчислення AST:\nІнтерпретація завершилась: {e}")

        tac_list = self.ir_gen.generate(folded_ast)
        tac_str = self.ir_gen.get_listing()

        asm_str = self.x86_gen.generate(tac_list)

        py_str = self.translator.to_python(folded_ast)
        js_str = self.translator.to_javascript(folded_ast)

        ast_dict = folded_ast.to_dict()

        payload = {
            "source": source_code,
            "tac": tac_str,
            "asm": asm_str,
            "python": py_str,
            "javascript": js_str,
            "semantics": "\n".join(sem_lines),
            "ast": ast_dict
        }

        out_path = os.path.join(self.visualizer_dir, output_json_name)
        os.makedirs(self.visualizer_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        js_data_path = os.path.join(self.visualizer_dir, "ast_data.js")
        with open(js_data_path, "w", encoding="utf-8") as f:
            f.write("window.AST_DATA = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n")

        return payload

    def open_in_browser(self):
        html_path = os.path.join(self.visualizer_dir, "index.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file:///{os.path.abspath(html_path).replace(chr(92), '/')}")
