import itertools


class Symbol:
    def __init__(self, name, sym_type, scope, node_id, extra=None):
        self.name = name
        self.type = sym_type  # "var", "func", "proc"
        self.scope = scope  # which scope owns this
        self.node_id = node_id
        self.extra = extra or {}  # for params, return type, etc.

    def __repr__(self):
        return f"{self.type.upper()} {self.name} (scope={self.scope}, node_id{self.node_id}, extra={self.extra})"


class SymbolTable:
    _id_counter = itertools.count()

    def __init__(self, scope_name="everywhere", parent=None):
        self.scope_name = scope_name
        self.parent = parent
        self.parent = parent
        self.symbols = {}  # dict: name -> Symbol
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
        """Lookup symbol by crawling up the scope chain"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None

    def create_child_scope(self, name):
        child = SymbolTable(scope_name=name, parent=self)
        self.children.append(child)
        return child

    def __repr__(self):
        out = f"\n[Scope: {self.scope_name}]\n"
        for sym in self.symbols.values():
            out += f"  {sym}\n"
        for c in self.children:
            out += repr(c)
        return out


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
    print(root.lookup("x"))  # global var
    print(func_scope.lookup("a"))  # local param
    print(proc_scope.lookup("y"))  # fallback to global
    print(proc_scope.lookup("z"))  # None ->underfined

    # Print everything
    print(root)
