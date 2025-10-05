# test_type_checker.py
from symbol_table import SymbolTable
from syntax_tree import ASTNode, ProgramNode, VarDeclNode, FuncNode, ProcNode
from type_checker import TypeChecker

# Helper that accepts 'children=' as used below
def N(t, val=None, children=None):
    return ASTNode(t, val, children or [])

def make_ok_program():
    # GLOBALS: var { x }
    globals_node = N("GLOBALS", children=[VarDeclNode("x")])

    # PROCS: none
    procs_node = N("PROCS", children=[])

    # FUNCS: func add(a,b) { local {} ; print "ok" } ; return 1
    params = [VarDeclNode("a"), VarDeclNode("b")]
    locals_block = N("LOCALS_BLOCK", children=[])  # 0..3 locals
    body_algo = N("ALGO", children=[
        N("PRINT", children=[N("STRING", "ok")]),
    ])
    body = N("BODY", children=[locals_block, body_algo])

    # Build a FUNC node the way the checker expects:
    func_with_return = N("FUNC", "add", children=params + [body, N("NUMBER", 1)])
    funcs_node = N("FUNCS", children=[func_with_return])

    # MAIN: var { c } ; c = (3 plus 4) ; if (c > 0) { print "yay" } else { print c } ; halt
    main_vars = N("VARS_BLOCK", children=[VarDeclNode("c")])

    assign_c = N("ASSIGN_EXPR", children=[
        N("VAR", "c"),
        N("BINOP", "plus", children=[N("NUMBER", 3), N("NUMBER", 4)])
    ])

    cond = N("BINOP", ">", children=[N("VAR", "c"), N("NUMBER", 0)])
    then_algo = N("ALGO", children=[N("PRINT", children=[N("STRING", "yay")])])
    else_algo = N("ALGO", children=[N("PRINT", children=[N("VAR", "c")])])
    if_stmt = N("IF", children=[cond, then_algo, else_algo])

    halt = N("HALT")
    main_algo = N("ALGO", children=[assign_c, if_stmt, halt])
    main_node = N("MAIN", children=[main_vars, main_algo])

    # PROGRAM
    prog = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    return prog

def make_bad_program():
    # GLOBALS: var { p }
    globals_node = N("GLOBALS", children=[VarDeclNode("p")])

    # PROC named 'p' (violates "typeless" — collides with global 'p')
    proc_body = N("BODY", children=[
        N("LOCALS_BLOCK", children=[]),
        N("ALGO", children=[N("PRINT", children=[N("VAR", "q")]), N("HALT")])
    ])
    bad_proc = N("PROC", "p", children=[VarDeclNode("q"), proc_body])
    procs_node = N("PROCS", children=[bad_proc])

    # FUNC sum(x,y) { local {} ; print "ok" } ; return z (undeclared)
    func_body = N("BODY", children=[
        N("LOCALS_BLOCK", children=[]),
        N("ALGO", children=[N("PRINT", children=[N("STRING", "ok")])])
    ])
    bad_func = N("FUNC", "sum", children=[VarDeclNode("x"), VarDeclNode("y"), func_body, N("VAR", "z")])
    funcs_node = N("FUNCS", children=[bad_func])

    # MAIN: var { p } ; p = (1 and 2) ; do { print p } until (1 eq 1)
    main_vars = N("VARS_BLOCK", children=[VarDeclNode("p")])
    assign_bad = N("ASSIGN_EXPR", children=[
        N("VAR", "p"),
        N("BINOP", "and", children=[N("NUMBER", 1), N("NUMBER", 2)])
    ])
    do_body = N("ALGO", children=[N("PRINT", children=[N("VAR", "p")])])
    do_until = N("DO_UNTIL", children=[do_body, N("BINOP", "eq", children=[N("NUMBER", 1), N("NUMBER", 1)])])
    main_algo = N("ALGO", children=[assign_bad, do_until])
    main_node = N("MAIN", children=[main_vars, main_algo])

    prog = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    return prog

if __name__ == "__main__":
    print("=== OK PROGRAM ===")
    root = SymbolTable("everywhere")
    checker = TypeChecker(root)
    ok_prog = make_ok_program()
    rep_ok = checker.check_program(ok_prog)
    print(rep_ok.ok)
    print("OK" if rep_ok.ok else "\n".join(rep_ok.errors))

    print("\n=== BAD PROGRAM ===")
    root2 = SymbolTable("everywhere")
    checker2 = TypeChecker(root2)
    bad_prog = make_bad_program()
    rep_bad = checker2.check_program(bad_prog)
    print(rep_bad.ok)
    for e in rep_bad.errors:
        print("-", e)
