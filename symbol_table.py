import itertools


class Symbol:
    def __init__(self, name, sym_type, scope, node_id, extra=None):
        self.name = name
        self.type = sym_type  # "var", "func", "proc"
        self.scope = scope
        self.node_id = node_id
        self.extra = extra or {}

    def to_row(self):
        extras = (
            ", ".join(f"{k}={v}" for k, v in self.extra.items()) if self.extra else ""
        )
        return [self.name, self.type.upper(), str(self.node_id), extras]


class SymbolTable:
    _id_counter = itertools.count()

    def __init__(self, scope_name="everywhere", parent=None):
        self.scope_name = scope_name
        self.parent = parent
        self.symbols = {}  # name -> Symbol
        self.children = []

    def add(self, name, sym_type, node_id=None, extra=None):
        if name in self.symbols:
            raise Exception(
                f"[Name-Rule-Violation] '{name}' already declared in scope '{self.scope_name}'"
            )
        self.symbols[name] = Symbol(
            name, sym_type, self.scope_name, node_id or next(self._id_counter), extra
        )

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None

    def create_child_scope(self, name):
        child = SymbolTable(scope_name=name, parent=self)
        self.children.append(child)
        return child

    def pretty_print(self, indent=0):
        pad = "  " * indent
        out = f"\n"
        out += f"{pad}Scope: {self.scope_name}\n"
        if self.symbols:
            col_names = ["Name", "Type", "ID", "Extra"]
            # Determine column widths
            rows = [sym.to_row() for sym in self.symbols.values()]
            widths = [
                max(len(str(cell)) for cell in [col] + [row[i] for row in rows])
                for i, col in enumerate(col_names)
            ]
            # Header
            header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(col_names))
            out += pad + header + "\n"
            out += pad + "-+-".join("-" * w for w in widths) + "\n"
            # Rows
            for row in rows:
                out += (
                    pad
                    + " | ".join(row[i].ljust(widths[i]) for i in range(len(col_names)))
                    + "\n"
                )
        else:
            out += pad + "(no symbols)\n"
        for c in self.children:
            out += c.pretty_print(indent + 1)
        return out

    def __repr__(self):
        return self.pretty_print()


def build_symbol_table(ast_root):
    """Builds a symbol table from AST (simplified version)."""
    root = SymbolTable("everywhere")

    # global scope
    globals_scope = root.create_child_scope("global")
    for child in ast_root.children[0].children:  # GLOBALS
        globals_scope.add(child.value, "var", node_id=child.id)

    # main scope
    main_scope = root.create_child_scope("main")
    vars_node, algo_node = ast_root.children[3].children
    for child in vars_node.children:  # VARS
        main_scope.add(child.value, "var", node_id=child.id)

    return root


# Debugging/demo
if __name__ == "__main__":
    # Root "everywhere"
    root = SymbolTable("everywhere")

    # Add global vars
    globals_scope = root.create_child_scope("global")
    globals_scope.add("x", "var")
    globals_scope.add("y", "var")

    # Add a function with local scope
    func_scope = root.create_child_scope("function myFunc")
    func_scope.add("myFunc", "func", extra={"params": ["a"], "return": "int"})
    func_scope.add("a", "var")
    func_scope.add("temp", "var")

    # Add a procedure with params
    proc_scope = root.create_child_scope("procedure myProc")
    proc_scope.add("myProc", "proc", extra={"params": ["p1"]})
    proc_scope.add("p1", "var")
    proc_scope.add("localVar", "var")

    # Test lookups
    print(root.lookup("x"))  # global var (Symbol or None)
    print(func_scope.lookup("a"))  # local param
    print(proc_scope.lookup("y"))  # fallback to global
    print(proc_scope.lookup("z"))  # None -> undeclared

    # Print everything
    print(root)
