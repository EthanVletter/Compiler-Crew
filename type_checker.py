from typing import Optional, List


# Small diagnostics helper
class TypeErrorReport:
    def __init__(self) -> None:
        self.errors: List[str] = []

    def add(self, msg: str) -> None:
        self.errors.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def __str__(self) -> str:
        if self.ok:
            return "OK"
        return "Type errors:\n- " + "\n- ".join(self.errors)


# Constants for "types"
NUMERIC = "numeric"
BOOLEAN = "boolean"


# Utilities: symbol table adapters
def _is_typeless(scope, name: str) -> bool:
    """True if name is NOT present in symbol tables (required for NAME in calls/defs)."""
    return scope.lookup(name) is None


def _declare_var(
    scope, name: str, report: TypeErrorReport, ctx: str, node_id=None
) -> None:
    """Declare a numeric variable in the current scope (collect duplicate errors)."""
    try:
        scope.add(name, "var", node_id=node_id)
    except Exception as e:
        report.add(f"{ctx}: {e}")


def _require_var(scope, name: str, report: TypeErrorReport, ctx: str) -> bool:
    """Ensure name exists and is a variable; return True if OK."""
    sym = scope.lookup(name)
    if sym is None:
        report.add(f"{ctx}: undeclared variable '{name}'")
        return False
    if sym.type != "var":
        report.add(f"{ctx}: '{name}' is a {sym.type}, not a variable")
        return False
    return True


# The Type Checker
class TypeChecker:

    def __init__(self, root_scope):
        self.report = TypeErrorReport()
        self.scopes = [root_scope]  # stack of SymbolTable scopes

    # ----- scope helpers -----
    @property
    def scope(self):
        return self.scopes[-1]

    def push_scope(self, name: str):
        child = self.scope.create_child_scope(name)
        self.scopes.append(child)

    def pop_scope(self):
        self.scopes.pop()

    # ----- ATOM & TERM typing -----
    def type_atom(self, node) -> Optional[str]:
        t = node.type
        if t == "VAR":
            ok = _require_var(self.scope, node.value, self.report, f"VAR(id={node.id})")
            return NUMERIC if ok else None
        if t == "NUMBER":
            return NUMERIC
        if t in ("BOOL", "TRUE", "FALSE"):
            # defensively allow different boolean literal spellings
            return BOOLEAN
        if t == "OUTPUT_ATOM":
            return self.type_atom(node.children[0])
        if t == "STRING":
            # strings are only valid when printed; not an ATOM in expressions
            self.report.add(f"STRING used where ATOM expected (id={node.id})")
            return None
        self.report.add(f"Unknown ATOM node '{t}' at id={node.id}")
        return None

    def type_term(self, node) -> Optional[str]:
        t = node.type

        # Bare atoms count as terms
        if t in ("VAR", "NUMBER", "BOOL", "TRUE", "FALSE", "OUTPUT_ATOM"):
            return self.type_atom(node)

        if t == "UNOP":
            op = node.value
            rhs_t = self.type_term(node.children[0])
            if op == "neg":
                if rhs_t == NUMERIC:
                    return NUMERIC
                self.report.add(f"Unary 'neg' expects numeric (id={node.id})")
                return None
            if op == "not":
                if rhs_t == BOOLEAN:
                    return BOOLEAN
                self.report.add(f"Unary 'not' expects boolean (id={node.id})")
                return None
            self.report.add(f"Unknown UNOP '{op}' (id={node.id})")
            return None

        if t == "BINOP":
            op = node.value
            lt = self.type_term(node.children[0])
            rt = self.type_term(node.children[1])
            if op in ("plus", "minus", "mult", "div"):
                if lt == NUMERIC and rt == NUMERIC:
                    return NUMERIC
                self.report.add(
                    f"Operator '{op}' requires numeric operands (id={node.id})"
                )
                return None
            if op in ("and", "or"):
                if lt == BOOLEAN and rt == BOOLEAN:
                    return BOOLEAN
                self.report.add(
                    f"Operator '{op}' requires boolean operands (id={node.id})"
                )
                return None
            if op in (">", "eq"):
                if lt == NUMERIC and rt == NUMERIC:
                    return BOOLEAN
                self.report.add(
                    f"Operator '{op}' requires numeric operands (id={node.id})"
                )
                return None
            self.report.add(f"Unknown BINOP '{op}' (id={node.id})")
            return None

        if t == "TERM" and node.children:
            # pass-through wrapper
            return self.type_term(node.children[0])

        self.report.add(f"Unknown TERM node '{t}' at id={node.id}")
        return None

    # output and input functions
    def check_output(self, node, ctx: str):
        # Either PRINT STRING, or PRINT ATOM (numeric)
        t = node.type
        if t == "OUTPUT_STRING" or t == "STRING":
            return
        if t == "OUTPUT_ATOM":
            if self.type_atom(node.children[0]) != NUMERIC:
                self.report.add(f"{ctx}: output atom must be numeric")
            return
        if t in ("VAR", "NUMBER"):
            if self.type_atom(node) != NUMERIC:
                self.report.add(f"{ctx}: output atom must be numeric")
            return
        if t == "PRINT":
            self.check_output(node.children[0], ctx)
            return
        self.report.add(f"{ctx}: unknown OUTPUT node '{t}'")

    def check_input(self, node, ctx: str):
        # INPUT: children are ATOMs (0..3), all numeric
        if node.type == "INPUT":
            atoms = node.children
        else:
            # Be permissive if the caller passed just a node that wraps the atoms list
            atoms = node.children

        if len(atoms) > 3:
            self.report.add(f"{ctx}: at most 3 input atoms allowed (got {len(atoms)})")

        for a in atoms:
            if self.type_atom(a) != NUMERIC:
                self.report.add(f"{ctx}: input atoms must be numeric")

    # instr and algo functions
    def check_instr(self, node, ctx: str):
        t = node.type

        if t == "HALT":
            return

        if t == "PRINT":
            # children[0] = STRING or ATOM
            if node.children:
                child = node.children[0]
                # Handle VAR nodes in print statements
                if child.type == "VAR":
                    if not _require_var(
                        self.scope, child.value, self.report, f"{ctx}/print"
                    ):
                        return
                else:
                    self.check_output(child, f"{ctx}/print")
            else:
                self.report.add(f"{ctx}: PRINT has no expression to print")
            return

        if t == "CALL":  # value = NAME, children = [INPUT]
            name = node.value
            if not _is_typeless(self.scope, name):
                self.report.add(
                    f"{ctx}: procedure/function name '{name}' must be typeless"
                )
            if node.children:
                self.check_input(node.children[0], f"{ctx}/call-input")
            return

        if t == "ASSIGN_CALL":  # value = NAME, children = [VAR, INPUT]
            name = node.value
            var_node = node.children[0]
            input_node = node.children[1]
            if not _is_typeless(self.scope, name):
                self.report.add(
                    f"{ctx}: procedure/function name '{name}' must be typeless"
                )
            self.check_input(input_node, f"{ctx}/assign-call-input")
            if var_node.type != "VAR" or not _require_var(
                self.scope, var_node.value, self.report, f"{ctx}/target"
            ):
                return
            return

        if t == "ASSIGN_EXPR":  # children = [VAR, TERM]
            var_node = node.children[0]
            term_node = node.children[1]
            if self.type_term(term_node) != NUMERIC:
                self.report.add(f"{ctx}: right-hand side of assignment must be numeric")
            if var_node.type != "VAR" or not _require_var(
                self.scope, var_node.value, self.report, f"{ctx}/target"
            ):
                return
            return

        if t == "ASSIGN":  # Our AST creates ASSIGN nodes - children = [VAR, TERM]
            var_node = node.children[0]
            term_node = node.children[1]
            if self.type_term(term_node) != NUMERIC:
                self.report.add(f"{ctx}: right-hand side of assignment must be numeric")
            if var_node.type != "VAR" or not _require_var(
                self.scope, var_node.value, self.report, f"{ctx}/target"
            ):
                return
            return

        if t == "IF":
            cond = node.children[0]
            then_algo = node.children[1]
            else_algo = node.children[2] if len(node.children) > 2 else None
            if self.type_term(cond) != BOOLEAN:
                self.report.add(f"{ctx}: if condition must be boolean")
            self.push_scope("then")
            self.check_algo(then_algo, f"{ctx}/then")
            self.pop_scope()
            if else_algo is not None:
                self.push_scope("else")
                self.check_algo(else_algo, f"{ctx}/else")
                self.pop_scope()
            return

        if t == "WHILE":
            cond = node.children[0]
            body_algo = node.children[1]
            if self.type_term(cond) != BOOLEAN:
                self.report.add(f"{ctx}: while condition must be boolean")
            self.push_scope("while")
            self.check_algo(body_algo, f"{ctx}/while-body")
            self.pop_scope()
            return

        if t == "DO_UNTIL":
            body_algo = node.children[0]
            cond = node.children[1]
            self.push_scope("do")
            self.check_algo(body_algo, f"{ctx}/do-body")
            self.pop_scope()
            if self.type_term(cond) != BOOLEAN:
                self.report.add(f"{ctx}: do-until condition must be boolean")
            return

        if t == "LOOP":
            # Handle LOOP nodes containing WHILE
            if node.children and node.children[0].type == "WHILE":
                while_node = node.children[0]
                cond = while_node.children[0]
                body_algo = while_node.children[1]
                if self.type_term(cond) != BOOLEAN:
                    self.report.add(f"{ctx}: while condition must be boolean")
                self.push_scope("while")
                self.check_algo(body_algo, f"{ctx}/while-body")
                self.pop_scope()
            else:
                self.report.add(f"{ctx}: unknown LOOP structure")
            return

        if t == "BRANCH":
            # Handle BRANCH nodes containing IF
            if node.children and node.children[0].type == "IF":
                if_node = node.children[0]
                cond = if_node.children[0]
                then_algo = if_node.children[1]
                else_algo = if_node.children[2] if len(if_node.children) > 2 else None
                if self.type_term(cond) != BOOLEAN:
                    self.report.add(f"{ctx}: if condition must be boolean")
                self.push_scope("then")
                self.check_algo(then_algo, f"{ctx}/then")
                self.pop_scope()
                if else_algo is not None:
                    self.push_scope("else")
                    self.check_algo(else_algo, f"{ctx}/else")
                    self.pop_scope()
            else:
                self.report.add(f"{ctx}: unknown BRANCH structure")
            return

        if t == "RETURN":
            # Only valid inside FUNC bodies (presence validated elsewhere).
            if self.type_atom(node.children[0]) != NUMERIC:
                self.report.add(f"{ctx}: function return atom must be numeric")
            return

        self.report.add(f"{ctx}: unknown instruction '{t}'")

    def check_algo(self, node, ctx: str):
        # Must be an ALGO node containing >=1 instruction
        if node.type != "ALGO":
            self.report.add(f"{ctx}: expected ALGO node, got {node.type}")
            return

        if not node.children:
            self.report.add(f"{ctx}: ALGO must contain at least one instruction")
            return

        for i, instr in enumerate(node.children):
            self.check_instr(instr, f"{ctx}/instr[{i}]")

    # decl and body functions
    def check_maxthree_vars(self, var_nodes, ctx: str):
        # var_nodes: list of VAR decls (0..3)
        if len(var_nodes) > 3:
            self.report.add(
                f"{ctx}: at most 3 variables allowed (got {len(var_nodes)})"
            )
        seen = set()
        for vn in var_nodes:
            if vn.type != "VAR":
                self.report.add(f"{ctx}: expected VAR declaration node, got {vn.type}")
                continue
            name = vn.value
            if name in seen:
                self.report.add(
                    f"{ctx}: duplicate variable '{name}' in declaration list"
                )
            seen.add(name)
            _declare_var(self.scope, name, self.report, ctx, node_id=vn.id)

    def check_variables_block(self, var_nodes, ctx: str):
        # Arbitrary number of VAR decls in current scope
        seen = set()
        for vn in var_nodes:
            if vn.type != "VAR":
                self.report.add(f"{ctx}: expected VAR declaration node, got {vn.type}")
                continue
            name = vn.value
            if name in seen:
                self.report.add(f"{ctx}: duplicate variable '{name}' in same block")
            seen.add(name)
            _declare_var(self.scope, name, self.report, ctx, node_id=vn.id)

    def check_body(self, body_node, ctx: str):
        # BODY children = [LOCALS_BLOCK, ALGO]
        if body_node.type != "BODY" or len(body_node.children) < 2:
            self.report.add(f"{ctx}: malformed BODY")
            return
        locals_block = body_node.children[0]
        algo = body_node.children[1]
        local_vars = locals_block.children  # list of VAR nodes

        self.push_scope("body")
        self.check_maxthree_vars(local_vars, f"{ctx}/locals")
        self.check_algo(algo, f"{ctx}/algo")
        self.pop_scope()

    #  PROC / FUNC / MAIN / PROGRAM functions
    def check_proc(self, proc_node, ctx: str):
        # PROC: value=name, children = [PARAM(=VAR), ..., BODY]
        name = proc_node.value
        if not _is_typeless(self.scope, name):
            self.report.add(f"{ctx}: procedure name '{name}' must be typeless")
        if not proc_node.children:
            self.report.add(f"{ctx}: malformed PROC (missing children)")
            return

        params = proc_node.children[:-1]
        body = proc_node.children[-1]

        self.push_scope(f"proc {name}")
        self.check_maxthree_vars(params, f"{ctx}/params")
        self.check_body(body, f"{ctx}/body")
        self.pop_scope()

    def _check_func_return_presence(
        self, body_node, explicit_return_atom_node, ctx: str
    ) -> None:
        """
        Accept either:
          - FUNC(..., BODY, RETURN_ATOM)
          - or BODY's ALGO last instruction is RETURN(ATOM)

        If both are present, both must be numeric.
        """
        if explicit_return_atom_node is not None:
            if self.type_atom(explicit_return_atom_node) != NUMERIC:
                self.report.add(f"{ctx}: function return atom must be numeric")

        had_return_instr = False
        if body_node.type == "BODY" and len(body_node.children) >= 2:
            algo = body_node.children[1]
            if algo.children:
                last = algo.children[-1]
                if last.type == "RETURN":
                    had_return_instr = True
                    if self.type_atom(last.children[0]) != NUMERIC:
                        self.report.add(f"{ctx}: function return atom must be numeric")

        if explicit_return_atom_node is None and not had_return_instr:
            self.report.add(
                f"{ctx}: missing return atom (neither explicit return child nor RETURN instruction)"
            )

    def check_func(self, func_node, ctx: str):
        # FUNC: value=name, children = [PARAM(=VAR), ..., BODY, (optional) RETURN_ATOM]
        name = func_node.value
        if not _is_typeless(self.scope, name):
            self.report.add(f"{ctx}: function name '{name}' must be typeless")
        if not func_node.children:
            self.report.add(f"{ctx}: malformed FUNC (missing children)")
            return

        # Detect whether the last child is an explicit return atom or not
        if len(func_node.children) >= 2 and func_node.children[-1].type != "BODY":
            explicit_return_atom = func_node.children[-1]
            body = func_node.children[-2]
            params = func_node.children[:-2]
        else:
            explicit_return_atom = None
            body = func_node.children[-1]
            params = func_node.children[:-1]

        self.push_scope(f"func {name}")
        self.check_maxthree_vars(params, f"{ctx}/params")
        self.check_body(body, f"{ctx}/body")
        self._check_func_return_presence(body, explicit_return_atom, f"{ctx}/return")
        self.pop_scope()

    def check_main(self, main_node, ctx: str):
        # MAIN: children = [VARS_BLOCK, ALGO]
        if main_node.type != "MAIN" or len(main_node.children) < 2:
            self.report.add(f"{ctx}: malformed MAIN")
            return
        vars_block = main_node.children[0]
        algo = main_node.children[1]

        self.push_scope("main")
        self.check_variables_block(vars_block.children, f"{ctx}/vars")
        self.check_algo(algo, f"{ctx}/algo")
        self.pop_scope()

    def check_program(self, program_node):
        """
        PROGRAM children = [GLOBALS, PROCS, FUNCS, MAIN]
        GLOBALS.children = [VAR, VAR, ...]
        PROCS.children   = [PROC, ...]
        FUNCS.children   = [FUNC, ...]
        """
        if program_node.type != "PROGRAM" or len(program_node.children) != 4:
            self.report.add(
                "PROGRAM: malformed (expected 4 children: GLOBALS, PROCS, FUNCS, MAIN)"
            )
            return self.report

        globals_node, procs_node, funcs_node, main_node = program_node.children

        # globals
        self.push_scope("global")
        self.check_variables_block(globals_node.children, "globals")

        # procs
        for i, p in enumerate(procs_node.children):
            if p.type != "PROC":
                self.report.add(f"proc[{i}]: expected PROC node, got {p.type}")
                continue
            self.check_proc(p, f"proc[{i}]")

        # funcs
        for i, f in enumerate(funcs_node.children):
            if f.type != "FUNC":
                self.report.add(f"func[{i}]: expected FUNC node, got {f.type}")
                continue
            self.check_func(f, f"func[{i}]")

        # main
        self.check_main(main_node, "main")
        self.pop_scope()
        return self.report
