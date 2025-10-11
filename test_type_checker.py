from symbol_table import SymbolTable
from syntax_tree import ASTNode, ProgramNode, VarDeclNode
from type_checker import TypeChecker

try:
    import pytest  
except Exception:  
    pytest = None


# helper functions
def N(t, val=None, children=None):
    return ASTNode(t, val, children or [])


def run_check(program_node):
    root = SymbolTable("everywhere")
    checker = TypeChecker(root)
    report = checker.check_program(program_node)
    return report.ok, list(report.errors)


def print_report(title, ok, errors):
    print(f"\n=== {title} ===")
    print("OK:" if ok else "ERRORS:")
    if ok:
        print("  ✓ No type errors")
    else:
        for e in errors:
            print("  -", e)


def missing_substrings(errors, expected_substrings):
    missing = []
    for sub in expected_substrings:
        if not any(sub in e for e in errors):
            missing.append(sub)
    return missing


# Baseline programs 
def make_ok_program():
    globals_node = N("GLOBALS", children=[VarDeclNode("x")])
    procs_node = N("PROCS", children=[])

    params = [VarDeclNode("a"), VarDeclNode("b")]
    locals_block = N("LOCALS_BLOCK", children=[])
    body_algo = N("ALGO", children=[N("PRINT", children=[N("STRING", "ok")])])
    body = N("BODY", children=[locals_block, body_algo])
    func_with_return = N("FUNC", "add", children=params + [body, N("NUMBER", 1)])
    funcs_node = N("FUNCS", children=[func_with_return])

    main_vars = N("VARS_BLOCK", children=[VarDeclNode("c")])
    assign_c = N("ASSIGN_EXPR", children=[
        N("VAR", "c"),
        N("BINOP", "plus", children=[N("NUMBER", 3), N("NUMBER", 4)]),
    ])
    cond = N("BINOP", ">", children=[N("VAR", "c"), N("NUMBER", 0)])
    then_algo = N("ALGO", children=[N("PRINT", children=[N("STRING", "yay")])])
    else_algo = N("ALGO", children=[N("PRINT", children=[N("VAR", "c")])])
    if_stmt = N("IF", children=[cond, then_algo, else_algo])
    halt = N("HALT")
    main_algo = N("ALGO", children=[assign_c, if_stmt, halt])
    main_node = N("MAIN", children=[main_vars, main_algo])

    return ProgramNode(globals_node, procs_node, funcs_node, main_node)


def make_bad_program():
    globals_node = N("GLOBALS", children=[VarDeclNode("p")])

    proc_body = N("BODY", children=[
        N("LOCALS_BLOCK", children=[]),
        N("ALGO", children=[N("PRINT", children=[N("VAR", "q")]), N("HALT")]),
    ])
    bad_proc = N("PROC", "p", children=[VarDeclNode("q"), proc_body])
    procs_node = N("PROCS", children=[bad_proc])

    func_body = N("BODY", children=[
        N("LOCALS_BLOCK", children=[]),
        N("ALGO", children=[N("PRINT", children=[N("STRING", "ok")])]),
    ])
    bad_func = N("FUNC", "sum", children=[
        VarDeclNode("x"),
        VarDeclNode("y"),
        func_body,
        N("VAR", "z"),  # undeclared return atom
    ])
    funcs_node = N("FUNCS", children=[bad_func])

    main_vars = N("VARS_BLOCK", children=[VarDeclNode("p")])
    assign_bad = N("ASSIGN_EXPR", children=[
        N("VAR", "p"),
        N("BINOP", "and", children=[N("NUMBER", 1), N("NUMBER", 2)]),
    ])
    do_body = N("ALGO", children=[N("PRINT", children=[N("VAR", "p")])])
    do_until = N("DO_UNTIL", children=[do_body, N("BINOP", "eq", children=[N("NUMBER", 1), N("NUMBER", 1)])])
    main_algo = N("ALGO", children=[assign_bad, do_until])
    main_node = N("MAIN", children=[main_vars, main_algo])

    return ProgramNode(globals_node, procs_node, funcs_node, main_node)


# ------------- Edge-case builders -------------
def mk_prog(glob_vars, procs, funcs, main_instrs, main_vars=None):
    globals_node = N("GLOBALS", children=[VarDeclNode(v) for v in (glob_vars or [])])
    procs_node = N("PROCS", children=procs or [])
    funcs_node = N("FUNCS", children=funcs or [])
    if main_vars is None:
        main_vars = []
    main = N("MAIN", children=[N("VARS_BLOCK", children=[VarDeclNode(v) for v in main_vars]),
                               N("ALGO", children=main_instrs or [N("HALT")])])
    return ProgramNode(globals_node, procs_node, funcs_node, main)


def func_with_params_and_body(name, params_nodes, locals_nodes, algo_instrs, explicit_return_atom=None):
    body = N("BODY", children=[N("LOCALS_BLOCK", children=locals_nodes),
                               N("ALGO", children=algo_instrs)])
    kids = list(params_nodes) + [body]
    if explicit_return_atom is not None:
        kids.append(explicit_return_atom)
    return N("FUNC", name, children=kids)


def proc_with_params_and_body(name, params_nodes, locals_nodes, algo_instrs):
    body = N("BODY", children=[N("LOCALS_BLOCK", children=locals_nodes),
                               N("ALGO", children=algo_instrs)])
    return N("PROC", name, children=list(params_nodes) + [body])


# ------------- Baseline tests -------------
def test_ok_program_passes():
    ok, errors = run_check(make_ok_program())
    if not ok:
        print_report("OK PROGRAM (unexpected errors)", ok, errors)
    assert ok, "Expected OK program to have no type errors"


def test_bad_program_fails_with_key_errors():
    ok, errors = run_check(make_bad_program())
    print_report("BAD PROGRAM (expected errors)", ok, errors)
    assert not ok, "Expected BAD program to fail type checking"

    expected = [
        "proc[0]: procedure name 'p' must be typeless",
        "undeclared variable 'z'",
        "function return atom must be numeric",
        "main/algo/instr[0]: right-hand side of assignment must be numeric",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing expected errors:\n  - " + "\n  - ".join(miss))


# ------------- BAD edge-case tests -------------
def test_maxthree_params_and_duplicates():
    params = [VarDeclNode("a"), VarDeclNode("a"), VarDeclNode("b"), VarDeclNode("c"), VarDeclNode("d")]
    f = func_with_params_and_body("f", params, [], [N("HALT")], explicit_return_atom=N("NUMBER", 1))
    prog = mk_prog([], [], [f], main_instrs=[N("HALT")])
    ok, errors = run_check(prog)
    print_report("MAXTHREE PARAMS", ok, errors)
    assert not ok
    expected = [
        "func[0]/params: at most 3 variables allowed",
        "func[0]/params: duplicate variable 'a' in declaration list",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_maxthree_locals_and_duplicates():
    locals_nodes = [VarDeclNode("a"), VarDeclNode("a"), VarDeclNode("b"), VarDeclNode("c"), VarDeclNode("d")]
    f = func_with_params_and_body("f", [], locals_nodes, [N("RETURN", children=[N("NUMBER", 0)])])
    prog = mk_prog([], [], [f], main_instrs=[N("HALT")])
    ok, errors = run_check(prog)
    print_report("MAXTHREE LOCALS", ok, errors)
    assert not ok
    expected = [
        "func[0]/body/locals: at most 3 variables allowed",
        "func[0]/body/locals: duplicate variable 'a' in declaration list",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_input_more_than_three_and_non_numeric():
    call = N("CALL", "g", children=[N("INPUT", children=[
        N("NUMBER", 1), N("NUMBER", 2), N("NUMBER", 3), N("BOOL", True)
    ])])
    prog = mk_prog([], [], [], main_instrs=[call, N("HALT")], main_vars=["x"])
    ok, errors = run_check(prog)
    print_report("INPUT EDGE CASES", ok, errors)
    assert not ok
    expected = [
        "main/algo/instr[0]/call-input: at most 3 input atoms allowed",
        "main/algo/instr[0]/call-input: input atoms must be numeric",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_print_undeclared_var_and_string_ok():
    instrs = [
        N("PRINT", children=[N("VAR", "y")]),  
        N("PRINT", children=[N("STRING", "ok")]),
        N("HALT"),
    ]
    prog = mk_prog(glob_vars=["x"], procs=[], funcs=[], main_instrs=instrs, main_vars=["x"])
    ok, errors = run_check(prog)
    print_report("PRINT EDGE CASES", ok, errors)
    assert not ok
    assert any("undeclared variable 'y'" in e for e in errors)


def test_if_while_do_conditions_must_be_boolean():
    if_stmt = N("IF", children=[N("NUMBER", 1), N("ALGO", children=[N("HALT")])])
    while_stmt = N("WHILE", children=[N("NUMBER", 0), N("ALGO", children=[N("HALT")])])
    do_until = N("DO_UNTIL", children=[N("ALGO", children=[N("HALT")]), N("NUMBER", 1)])
    prog = mk_prog([], [], [], main_instrs=[if_stmt, while_stmt, do_until, N("HALT")])
    ok, errors = run_check(prog)
    print_report("BOOLEAN CONDITIONS (BAD)", ok, errors)
    assert not ok
    expected = [
        "main/algo/instr[0]: if condition must be boolean",
        "main/algo/instr[1]: while condition must be boolean",
        "main/algo/instr[2]: do-until condition must be boolean",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_missing_return_and_non_numeric_return():
    f1 = func_with_params_and_body("f1", [], [], [N("PRINT", children=[N("STRING", "hi")])])
    f2 = func_with_params_and_body("f2", [], [], [N("HALT")], explicit_return_atom=N("BOOL", True))
    prog = mk_prog([], [], [f1, f2], main_instrs=[N("HALT")])
    ok, errors = run_check(prog)
    print_report("RETURN EDGE CASES (BAD)", ok, errors)
    assert not ok
    expected = [
        "func[0]/return: missing return atom",
        "func[1]/return: function return atom must be numeric",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_algo_node_required_in_body():
    bad_body = N("BODY", children=[N("LOCALS_BLOCK", children=[]), N("VAR", "x")])
    bad_proc = N("PROC", "q", children=[bad_body])
    prog = mk_prog([], [bad_proc], [], main_instrs=[N("HALT")])
    ok, errors = run_check(prog)
    print_report("ALGO NODE REQUIRED (BAD)", ok, errors)
    assert not ok
    assert any("proc[0]/body/algo: expected ALGO node" in e for e in errors)


def test_assignment_target_undeclared_and_term_type_error():
    assign = N("ASSIGN_EXPR", children=[
        N("VAR", "z"),
        N("BINOP", "and", children=[N("NUMBER", 1), N("NUMBER", 2)])
    ])
    prog = mk_prog([], [], [], main_instrs=[assign, N("HALT")], main_vars=[])
    ok, errors = run_check(prog)
    print_report("ASSIGNMENT EDGE CASES (BAD)", ok, errors)
    assert not ok
    expected = [
        "main/algo/instr[0]: right-hand side of assignment must be numeric",
        "main/algo/instr[0]/target: undeclared variable 'z'",
    ]
    miss = missing_substrings(errors, expected)
    if miss:
        raise AssertionError("Missing:\n  - " + "\n  - ".join(miss))


def test_call_name_must_be_typeless():
    call = N("CALL", "foo", children=[N("INPUT", children=[N("NUMBER", 1)])])
    prog = mk_prog(["foo"], [], [], main_instrs=[call, N("HALT")])
    ok, errors = run_check(prog)
    print_report("CALLEE NAME TYPELESS (BAD)", ok, errors)
    assert not ok
    assert any("procedure/function name 'foo' must be typeless" in e for e in errors)


# ------------- GOOD edge-case tests -------------
def test_good_maxthree_limits_and_no_duplicates():
    # func f(a,b,c) { local {u,v,w} ; return 0 }  -- exactly 3 params and 3 locals
    params = [VarDeclNode("a"), VarDeclNode("b"), VarDeclNode("c")]
    locals_nodes = [VarDeclNode("u"), VarDeclNode("v"), VarDeclNode("w")]
    algo = [N("RETURN", children=[N("NUMBER", 0)])]
    f = func_with_params_and_body("f", params, locals_nodes, algo)
    # main does a HALT
    prog = mk_prog([], [], [f], main_instrs=[N("HALT")], main_vars=[])
    ok, errors = run_check(prog)
    print_report("GOOD: MAXTHREE LIMITS", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_if_while_do_with_boolean_conditions():
    # c declared; conditions use comparisons producing boolean
    instrs = [
        N("ASSIGN_EXPR", children=[N("VAR", "c"), N("NUMBER", 5)]),
        N("IF", children=[
            N("BINOP", ">", children=[N("VAR", "c"), N("NUMBER", 1)]),
            N("ALGO", children=[N("PRINT", children=[N("STRING", "ok")])]),
            N("ALGO", children=[N("PRINT", children=[N("NUMBER", 0)])]),
        ]),
        N("WHILE", children=[
            N("BINOP", "eq", children=[N("NUMBER", 1), N("NUMBER", 1)]),
            N("ALGO", children=[N("HALT")]),
        ]),
        N("DO_UNTIL", children=[
            N("ALGO", children=[N("PRINT", children=[N("NUMBER", 7)])]),
            N("BINOP", "eq", children=[N("NUMBER", 2), N("NUMBER", 2)]),
        ]),
        N("HALT"),
    ]
    prog = mk_prog([], [], [], main_instrs=instrs, main_vars=["c"])
    ok, errors = run_check(prog)
    print_report("GOOD: BOOLEAN CONDITIONS", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_func_return_via_return_instruction():
    # No explicit atom child; return via RETURN(ATOM) in ALGO
    algo = [N("RETURN", children=[N("NUMBER", 123)])]
    f = func_with_params_and_body("g", [], [], algo) 
    prog = mk_prog([], [], [f], main_instrs=[N("HALT")])
    ok, errors = run_check(prog)
    print_report("GOOD: RETURN VIA INSTR", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_assign_call_with_numeric_inputs_and_declared_target():
    # Ensure NAME is typeless (not declared anywhere), 2 numeric inputs, target declared
    instrs = [
        N("ASSIGN_CALL", "someProc", children=[
            N("VAR", "d"),
            N("INPUT", children=[N("NUMBER", 1), N("NUMBER", 2)])
        ]),
        N("HALT"),
    ]
    prog = mk_prog([], [], [], main_instrs=instrs, main_vars=["d"])
    ok, errors = run_check(prog)
    print_report("GOOD: ASSIGN_CALL", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_scoping_and_shadowing():
    # Global x; main declares its own x (shadowing is fine)
    # IF/ELSE introduce inner scopes and use variables correctly.
    instrs = [
        N("ASSIGN_EXPR", children=[N("VAR", "x"), N("NUMBER", 10)]),
        N("IF", children=[
            N("BINOP", ">", children=[N("VAR", "x"), N("NUMBER", 0)]),
            N("ALGO", children=[
                N("ASSIGN_EXPR", children=[N("VAR", "x"), N("BINOP", "plus", children=[N("VAR", "x"), N("NUMBER", 1)])]),
                N("PRINT", children=[N("VAR", "x")]),
            ]),
            N("ALGO", children=[
                N("PRINT", children=[N("NUMBER", 0)]),
            ]),
        ]),
        N("HALT"),
    ]
    prog = mk_prog(glob_vars=["x"], procs=[], funcs=[], main_instrs=instrs, main_vars=["x"])
    ok, errors = run_check(prog)
    print_report("GOOD: SCOPING/SHADOWING", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_print_numeric_atoms_and_binops():
    # print number; print var; use plus/mult/div/minus well-typed
    instrs = [
        N("ASSIGN_EXPR", children=[N("VAR", "a"), N("BINOP", "plus", children=[N("NUMBER", 2), N("NUMBER", 3)])]),
        N("PRINT", children=[N("VAR", "a")]),
        N("PRINT", children=[N("NUMBER", 99)]),
        N("ASSIGN_EXPR", children=[N("VAR", "b"),
                                   N("BINOP", "div", children=[
                                       N("BINOP", "mult", children=[N("NUMBER", 8), N("NUMBER", 5)]),
                                       N("BINOP", "minus", children=[N("NUMBER", 7), N("NUMBER", 1)])
                                   ])]),
        N("HALT"),
    ]
    prog = mk_prog([], [], [], main_instrs=instrs, main_vars=["a", "b"])
    ok, errors = run_check(prog)
    print_report("GOOD: PRINT & BINOPS", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


def test_good_unary_ops_types():
    instrs = [
        N("IF", children=[
            N("UNOP", "not", children=[N("BOOL", True)]),
            N("ALGO", children=[N("HALT")]),
            N("ALGO", children=[N("HALT")]),
        ]),
        N("ASSIGN_EXPR", children=[N("VAR", "m"), N("UNOP", "neg", children=[N("NUMBER", 4)])]),
        N("HALT"),
    ]
    prog = mk_prog([], [], [], main_instrs=instrs, main_vars=["m"])
    ok, errors = run_check(prog)
    print_report("GOOD: UNARY OPS", ok, errors)
    assert ok, f"Expected pass, got errors: {errors}"


# ------------- __main__ runner -------------
if __name__ == "__main__":
    tests = [
        # Baseline
        test_ok_program_passes,
        test_bad_program_fails_with_key_errors,
        # BAD edge cases
        test_maxthree_params_and_duplicates,
        test_maxthree_locals_and_duplicates,
        test_input_more_than_three_and_non_numeric,
        test_print_undeclared_var_and_string_ok,
        test_if_while_do_conditions_must_be_boolean,
        test_missing_return_and_non_numeric_return,
        test_algo_node_required_in_body,
        test_assignment_target_undeclared_and_term_type_error,
        test_call_name_must_be_typeless,
        # GOOD edge cases
        test_good_maxthree_limits_and_no_duplicates,
        test_good_if_while_do_with_boolean_conditions,
        test_good_func_return_via_return_instruction,
        test_good_assign_call_with_numeric_inputs_and_declared_target,
        test_good_scoping_and_shadowing,
        test_good_print_numeric_atoms_and_binops,
        test_good_unary_ops_types,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"\n[FAIL] {t.__name__}: {e}")
    if failures:
        print(f"\nSummary: {len(tests)-failures} passed, {failures} failed")
        import sys
        sys.exit(1)
    else:
        print(f"\nSummary: {len(tests)} passed, 0 failed ")
