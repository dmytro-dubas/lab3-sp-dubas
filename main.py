
import sys
import os
import argparse

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from py_compiler import (
    CParser, SemanticAnalyzer, ASTInterpreter,
    IRGenerator, X86CodeGenerator, TargetTranslator, ASTVisualizerService
)

def main():
    parser = argparse.ArgumentParser(description="C subset compiler and AST analyzer")
    parser.add_argument("source_file", nargs="?", default="examples/01_arithmetic_constant_folding.c",
                        help="Path to C source file")
    parser.add_argument("--ast", action="store_true", help="Print AST")
    parser.add_argument("--folded-ast", action="store_true", help="Print folded AST")
    parser.add_argument("--ir", "--tac", dest="ir", action="store_true", help="Print 3AC IR")
    parser.add_argument("--asm", action="store_true", help="Print x86-64 assembly")
    parser.add_argument("--translate", action="store_true", help="Print Python and JavaScript translation")
    parser.add_argument("--eval", action="store_true", help="Execute AST")
    parser.add_argument("--visualize", "-v", action="store_true", help="Open D3.js visualization in browser")
    parser.add_argument("--all", action="store_true", help="Run all compiler phases and print output")

    args = parser.parse_args()

    if not os.path.exists(args.source_file):
        print(f"Error: file '{args.source_file}' not found", file=sys.stderr)
        sys.exit(1)

    with open(args.source_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    print(f"File: {args.source_file}")

    c_parser = CParser()
    try:
        raw_ast = c_parser.parse(source_code)
        print("Parser: OK")
    except Exception as e:
        print(f"Parser error: {e}", file=sys.stderr)
        sys.exit(1)

    folded_ast = raw_ast.fold()
    print("Constant folding: OK")

    analyzer = SemanticAnalyzer()
    diagnostics = analyzer.analyze(folded_ast)
    err_count = sum(1 for d in diagnostics if d.severity == "ERROR")
    warn_count = sum(1 for d in diagnostics if d.severity == "WARNING")
    print(f"Semantics: {err_count} errors, {warn_count} warnings")

    for d in diagnostics:
        print(f"  [{d.severity}] line {d.line}: {d.message}")

    interpreter = ASTInterpreter()
    exec_result = None
    try:
        exec_result = interpreter.execute(folded_ast)
        print(f"Eval result: {exec_result}")
    except Exception as e:
        print(f"Eval note: {e}")

    ir_gen = IRGenerator()
    tac_list = ir_gen.generate(folded_ast)
    print(f"3AC generation: OK ({len(tac_list)} instructions)")

    x86_gen = X86CodeGenerator()
    asm_code = x86_gen.generate(tac_list)
    print("x86-64 codegen: OK")

    translator = TargetTranslator()
    py_code = translator.to_python(folded_ast)
    js_code = translator.to_javascript(folded_ast)
    print("Target translation: OK")

    viz_service = ASTVisualizerService()
    if args.visualize or args.all:
        viz_service.compile_and_export(source_code)

    if args.all or args.ast:
        print("\n[AST]")
        print(raw_ast.pretty())

    if args.all or args.folded_ast:
        print("\n[Folded AST]")
        print(folded_ast.pretty())

    if args.all or args.ir:
        print("\n[3AC IR]")
        print(ir_gen.get_listing())

    if args.all or args.asm:
        print("\n[x86-64 ASM]")
        print(asm_code)

    if args.all or args.translate:
        print("\n[Python Translation]")
        print(py_code)
        print("\n[JavaScript Translation]")
        print(js_code)

    if args.visualize:
        viz_service.open_in_browser()

if __name__ == "__main__":
    main()
