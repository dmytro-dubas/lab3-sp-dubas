
import sys
import os
import unittest
import time
import glob

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    start_time = time.time()
    test_loader = unittest.TestLoader()
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    suite = test_loader.discover(start_dir=test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print(f"\nUnit tests: {result.testsRun} run in {elapsed:.3f}s (errors={len(result.errors)}, failures={len(result.failures)})")

    from py_compiler import CParser, SemanticAnalyzer, ASTInterpreter, TargetTranslator
    parser = CParser()
    analyzer = SemanticAnalyzer()
    interpreter = ASTInterpreter()
    translator = TargetTranslator()

    example_files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "examples", "*.c")))
    all_examples_ok = True

    print("\nChecking examples:")
    for ef in example_files:
        fname = os.path.basename(ef)
        try:
            with open(ef, "r", encoding="utf-8") as f:
                code = f.read()
            ast = parser.parse(code)
            folded = ast.fold()
            diags = analyzer.analyze(folded)
            res = interpreter.execute(folded)
            translator.to_python(folded)
            translator.to_javascript(folded)

            err_diags = [d for d in diags if d.severity == "ERROR"]
            if err_diags:
                print(f"  FAIL: {fname} ({len(err_diags)} errors)")
                all_examples_ok = False
            else:
                print(f"  OK: {fname} (result: {res})")
        except Exception as e:
            print(f"  FAIL: {fname} ({e})")
            all_examples_ok = False

    if result.wasSuccessful() and all_examples_ok:
        print("\nAll tests passed.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
