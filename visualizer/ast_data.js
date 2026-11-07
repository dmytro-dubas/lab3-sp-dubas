window.AST_DATA = {
  "source": "int main() {\n    int folded_val = 2 + 3 * 4;\n    int complex_fold = (10 - 4) * (8 / 2) + (15 % 4);\n    int a = 15;\n    int b = 4;\n    int c = a + b * 2;\n    int logic_test = (a > b) && (c == 23) || (b <= 0);\n    return complex_fold + c;\n}\n",
  "tac": "\nfunc_main:\n  folded_val = 14\n  complex_fold = 27\n  a = 15\n  b = 4\n  t1 = b * 2\n  t2 = a + t1\n  c = t2\n  t3 = a > b\n  t4 = c == 23\n  t5 = t3 && t4\n  t6 = b <= 0\n  t7 = t5 || t6\n  logic_test = t7\n  t8 = complex_fold + c\n  return t8\n",
  "asm": ".intel_syntax noprefix\n.text\n\n.globl main\n.type main, @function\nmain:\n    push rbp\n    mov rbp, rsp\n    sub rsp, 112\n    mov eax, 14\n    mov DWORD PTR [rbp - 8], eax\n    mov eax, 27\n    mov DWORD PTR [rbp - 16], eax\n    mov eax, 15\n    mov DWORD PTR [rbp - 24], eax\n    mov eax, 4\n    mov DWORD PTR [rbp - 32], eax\n    mov eax, DWORD PTR [rbp - 32]\n    mov ebx, 2\n    imul eax, ebx\n    mov DWORD PTR [rbp - 40], eax\n    mov eax, DWORD PTR [rbp - 24]\n    mov ebx, DWORD PTR [rbp - 40]\n    add eax, ebx\n    mov DWORD PTR [rbp - 48], eax\n    mov eax, DWORD PTR [rbp - 48]\n    mov DWORD PTR [rbp - 56], eax\n    mov eax, DWORD PTR [rbp - 24]\n    mov ebx, DWORD PTR [rbp - 32]\n    cmp eax, ebx\n    setg al\n    movzx eax, al\n    mov DWORD PTR [rbp - 64], eax\n    mov eax, DWORD PTR [rbp - 56]\n    mov ebx, 23\n    cmp eax, ebx\n    sete al\n    movzx eax, al\n    mov DWORD PTR [rbp - 72], eax\n    mov eax, DWORD PTR [rbp - 64]\n    mov ebx, DWORD PTR [rbp - 72]\n    and eax, ebx\n    setne al\n    movzx eax, al\n    mov DWORD PTR [rbp - 80], eax\n    mov eax, DWORD PTR [rbp - 32]\n    mov ebx, 0\n    cmp eax, ebx\n    setle al\n    movzx eax, al\n    mov DWORD PTR [rbp - 88], eax\n    mov eax, DWORD PTR [rbp - 80]\n    mov ebx, DWORD PTR [rbp - 88]\n    or eax, ebx\n    setne al\n    movzx eax, al\n    mov DWORD PTR [rbp - 96], eax\n    mov eax, DWORD PTR [rbp - 96]\n    mov DWORD PTR [rbp - 104], eax\n    mov eax, DWORD PTR [rbp - 16]\n    mov ebx, DWORD PTR [rbp - 56]\n    add eax, ebx\n    mov DWORD PTR [rbp - 112], eax\n    mov eax, DWORD PTR [rbp - 112]\n    leave\n    ret\n.size main, .-main",
  "python": "def main():\n    folded_val = 14\n    complex_fold = 27\n    a = 15\n    b = 4\n    c = (a + (b * 2))\n    logic_test = (((a > b) and (c == 23)) or (b <= 0))\n    return (complex_fold + c)\n\n\nif __name__ == '__main__':\n    if 'main' in globals():\n        result = main()\n        print(f'Результат виконання трансляції main(): {result}')",
  "javascript": "function main() {\n  let folded_val = 14;\n  let complex_fold = 27;\n  let a = 15;\n  let b = 4;\n  let c = (a + (b * 2));\n  let logic_test = (((a > b) && (c == 23)) || (b <= 0));\n  return (complex_fold + c);\n}\n\nif (typeof main === 'function') {\n    console.log('Результат виконання трансляції main():', main());\n}",
  "semantics": "Семантичний аналіз:\nСтатус: успішно (0 помилок)\n\nГлобальна таблиця символів:\n  - main: int (func)\n\nОбчислення AST:\nРезультат виконання main(): 50",
  "ast": {
    "name": "TranslationUnit (AST Root)",
    "type": "Program",
    "category": "root",
    "children": [
      {
        "name": "Function: int main()",
        "type": "FunctionDef",
        "returnType": "int",
        "funcName": "main",
        "category": "function",
        "children": [
          {
            "name": "Params (0)",
            "type": "ParamList",
            "category": "declaration",
            "children": []
          },
          {
            "name": "Block { ... }",
            "type": "CompoundStmt",
            "category": "structure",
            "children": [
              {
                "name": "VarDecl: int folded_val",
                "type": "VarDecl",
                "varType": "int",
                "varName": "folded_val",
                "category": "declaration",
                "children": [
                  {
                    "name": "Literal: 14",
                    "type": "Literal",
                    "val": 14,
                    "category": "literal",
                    "dataType": "int",
                    "children": []
                  }
                ]
              },
              {
                "name": "VarDecl: int complex_fold",
                "type": "VarDecl",
                "varType": "int",
                "varName": "complex_fold",
                "category": "declaration",
                "children": [
                  {
                    "name": "Literal: 27",
                    "type": "Literal",
                    "val": 27,
                    "category": "literal",
                    "dataType": "int",
                    "children": []
                  }
                ]
              },
              {
                "name": "VarDecl: int a",
                "type": "VarDecl",
                "varType": "int",
                "varName": "a",
                "category": "declaration",
                "children": [
                  {
                    "name": "Literal: 15",
                    "type": "Literal",
                    "val": 15,
                    "category": "literal",
                    "dataType": "int",
                    "children": []
                  }
                ]
              },
              {
                "name": "VarDecl: int b",
                "type": "VarDecl",
                "varType": "int",
                "varName": "b",
                "category": "declaration",
                "children": [
                  {
                    "name": "Literal: 4",
                    "type": "Literal",
                    "val": 4,
                    "category": "literal",
                    "dataType": "int",
                    "children": []
                  }
                ]
              },
              {
                "name": "VarDecl: int c",
                "type": "VarDecl",
                "varType": "int",
                "varName": "c",
                "category": "declaration",
                "children": [
                  {
                    "name": "BinaryOp: +",
                    "type": "BinaryOp",
                    "op": "+",
                    "category": "operator",
                    "children": [
                      {
                        "name": "Id: a",
                        "type": "Identifier",
                        "val": "a",
                        "category": "identifier",
                        "children": []
                      },
                      {
                        "name": "BinaryOp: *",
                        "type": "BinaryOp",
                        "op": "*",
                        "category": "operator",
                        "children": [
                          {
                            "name": "Id: b",
                            "type": "Identifier",
                            "val": "b",
                            "category": "identifier",
                            "children": []
                          },
                          {
                            "name": "Literal: 2",
                            "type": "Literal",
                            "val": 2,
                            "category": "literal",
                            "dataType": "int",
                            "children": []
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "name": "VarDecl: int logic_test",
                "type": "VarDecl",
                "varType": "int",
                "varName": "logic_test",
                "category": "declaration",
                "children": [
                  {
                    "name": "BinaryOp: ||",
                    "type": "BinaryOp",
                    "op": "||",
                    "category": "operator",
                    "children": [
                      {
                        "name": "BinaryOp: &&",
                        "type": "BinaryOp",
                        "op": "&&",
                        "category": "operator",
                        "children": [
                          {
                            "name": "BinaryOp: >",
                            "type": "BinaryOp",
                            "op": ">",
                            "category": "operator",
                            "children": [
                              {
                                "name": "Id: a",
                                "type": "Identifier",
                                "val": "a",
                                "category": "identifier",
                                "children": []
                              },
                              {
                                "name": "Id: b",
                                "type": "Identifier",
                                "val": "b",
                                "category": "identifier",
                                "children": []
                              }
                            ]
                          },
                          {
                            "name": "BinaryOp: ==",
                            "type": "BinaryOp",
                            "op": "==",
                            "category": "operator",
                            "children": [
                              {
                                "name": "Id: c",
                                "type": "Identifier",
                                "val": "c",
                                "category": "identifier",
                                "children": []
                              },
                              {
                                "name": "Literal: 23",
                                "type": "Literal",
                                "val": 23,
                                "category": "literal",
                                "dataType": "int",
                                "children": []
                              }
                            ]
                          }
                        ]
                      },
                      {
                        "name": "BinaryOp: <=",
                        "type": "BinaryOp",
                        "op": "<=",
                        "category": "operator",
                        "children": [
                          {
                            "name": "Id: b",
                            "type": "Identifier",
                            "val": "b",
                            "category": "identifier",
                            "children": []
                          },
                          {
                            "name": "Literal: 0",
                            "type": "Literal",
                            "val": 0,
                            "category": "literal",
                            "dataType": "int",
                            "children": []
                          }
                        ]
                      }
                    ]
                  }
                ]
              },
              {
                "name": "Return",
                "type": "ReturnStmt",
                "category": "statement",
                "children": [
                  {
                    "name": "BinaryOp: +",
                    "type": "BinaryOp",
                    "op": "+",
                    "category": "operator",
                    "children": [
                      {
                        "name": "Id: complex_fold",
                        "type": "Identifier",
                        "val": "complex_fold",
                        "category": "identifier",
                        "children": []
                      },
                      {
                        "name": "Id: c",
                        "type": "Identifier",
                        "val": "c",
                        "category": "identifier",
                        "children": []
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
};
