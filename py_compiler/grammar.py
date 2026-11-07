
C_GRAMMAR = r'''
    ?start: translation_unit

    translation_unit: external_decl*

    ?external_decl: function_def
                  | var_decl

    function_def: type_spec IDENTIFIER "(" param_list? ")" compound_stmt

    var_decl: type_spec init_declarator_list ";"

    type_spec: "int"   -> type_int
             | "float" -> type_float
             | "void"  -> type_void

    param_list: "void"                     -> empty_param_list
              | param_decl ("," param_decl)*
    param_decl: type_spec IDENTIFIER

    init_declarator_list: init_declarator ("," init_declarator)*
    init_declarator: IDENTIFIER ("=" expr)?

    compound_stmt: "{" block_item* "}"

    ?block_item: var_decl
               | stmt

    ?stmt: compound_stmt
         | if_stmt
         | while_stmt
         | for_stmt
         | return_stmt
         | expr_stmt

    expr_stmt: expr? ";"

    if_stmt: "if" "(" expr ")" stmt "else" stmt -> if_else_stmt
           | "if" "(" expr ")" stmt             -> if_single_stmt

    while_stmt: "while" "(" expr ")" stmt

    for_stmt: "for" "(" for_init for_cond? ";" expr? ")" stmt
    for_init: var_decl   -> for_init_var
            | expr_stmt  -> for_init_expr
    for_cond: expr

    return_stmt: "return" expr? ";"

    ?expr: assignment

    ?assignment: IDENTIFIER "=" assignment -> assign
               | logical_or

    ?logical_or: logical_or "||" logical_and -> op_or
               | logical_and

    ?logical_and: logical_and "&&" equality  -> op_and
                | equality

    ?equality: equality "==" relational -> op_eq
             | equality "!=" relational -> op_ne
             | relational

    ?relational: relational "<" additive  -> op_lt
               | relational "<=" additive -> op_le
               | relational ">" additive  -> op_gt
               | relational ">=" additive -> op_ge
               | additive

    ?additive: additive "+" multiplicative -> op_add
             | additive "-" multiplicative -> op_sub
             | multiplicative

    ?multiplicative: multiplicative "*" unary -> op_mul
                   | multiplicative "/" unary -> op_div
                   | multiplicative "%" unary -> op_mod
                   | unary

    ?unary: "-" unary -> op_neg
          | "+" unary -> op_pos
          | "!" unary -> op_not
          | postfix

    ?postfix: IDENTIFIER "(" arg_list? ")" -> func_call
            | primary

    arg_list: expr ("," expr)*

    ?primary: IDENTIFIER -> var
            | NUMBER     -> number
            | "(" expr ")"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+(\.[0-9]+)?/

    %import common.WS
    %ignore WS

    COMMENT: "/*" /(.|\n)*?/ "*/"
    %ignore COMMENT

    LINE_COMMENT: "//" /[^\n]*/
    %ignore LINE_COMMENT
'''
