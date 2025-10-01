import itertools


class ASTNode:
    _id_counter = itertools.count()

    def __init__(self, nodetype, value=None, children=None):
        self.id = next(ASTNode._id_counter)
        self.type = nodetype  # e.g., "VAR", "FUNC", "PROC", "ASSIGN"
        self.value = value  # e.g., variable name, function name, number
        self.children = children or []

    def add_child(self, node):
        self.children.append(node)

    def pretty_print(self, indent=0):
        pad = "  " * indent
        val_str = f": {self.value}" if self.value is not None else ""
        s = f"{pad}{self.type}{val_str} (id={self.id})\n"
        for c in self.children:
            s += c.pretty_print(indent + 1)
        return s

    def __repr__(self):
        return f"<ASTNode {self.type} id={self.id}>"


# Node types
class ProgramNode(ASTNode):
    def __init__(self, globals_node, procs_node, funcs_node, main_node):
        super().__init__(
            "PROGRAM", children=[globals_node, procs_node, funcs_node, main_node]
        )


class VarDeclNode(ASTNode):
    def __init__(self, name):
        super().__init__("VAR", value=name)


class FuncNode(ASTNode):
    def __init__(self, name, params, body, ret_type):
        super().__init__("FUNC", value=name, children=params + [body])
        self.return_type = ret_type


class ProcNode(ASTNode):
    def __init__(self, name, params, body):
        super().__init__("PROC", value=name, children=params + [body])
