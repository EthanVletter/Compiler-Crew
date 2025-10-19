import itertools


class ASTNode:
    _id_counter = itertools.count()

    def __init__(self, nodetype, value=None, children=None):
        self.id = next(ASTNode._id_counter)
        self.type = nodetype
        self.value = value
        self.children = children or []

    def add_child(self, node):
        self.children.append(node)

    def pretty_print(self, prefix="", is_last=True):
        connector = "└─ " if is_last else "├─ "
        val_str = f": {self.value}" if self.value is not None else ""
        s = f"{prefix}{connector}{self.type}{val_str} (id={self.id})\n"

        # Update prefix for children
        if is_last:
            prefix += "   "
        else:
            prefix += "│  "

        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            s += child.pretty_print(prefix, last)
        return s

    def __repr__(self):
        return f"<ASTNode {self.type} id={self.id}>"


# ---------------- Node types ----------------
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


def build_ast(tokens):
    """Builds and populates a complete AST from the given token list."""
    # 1. Create empty containers for main sections
    globals_node = ASTNode("GLOBALS")
    procs_node = ASTNode("PROCS")
    funcs_node = ASTNode("FUNCS")
    main_node = ASTNode("MAIN")

    # 2. Create the root program node
    program_node = ProgramNode(
        globals_node=globals_node,
        procs_node=procs_node,
        funcs_node=funcs_node,
        main_node=main_node,
    )

    # 3. Internal state
    current_section = None
    var_block_active = False
    algo_node = None
    vars_node = None

    # 4. Go through tokens
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        # Detect which section we're in
        if tok.type.upper() == "GLOB":
            current_section = globals_node
        elif tok.type.upper() == "PROC":
            current_section = procs_node
        elif tok.type.upper() == "FUNC":
            current_section = funcs_node
        elif tok.type.upper() == "MAIN":
            current_section = main_node

        # Handle global vars (inside glob { ... })
        elif tok.type.upper() == "IDENT" and current_section == globals_node:
            var_decl = VarDeclNode(tok.value)
            globals_node.add_child(var_decl)

        # Handle main vars
        elif tok.type.upper() == "VAR" and current_section == main_node:
            var_block_active = True
            vars_node = ASTNode("VARS")
            current_section.add_child(vars_node)

        elif var_block_active and tok.type.upper() == "IDENT":
            var_decl = VarDeclNode(tok.value)
            vars_node.add_child(var_decl)

        elif tok.type.upper() == "RBRACE" and var_block_active:
            var_block_active = False

        # Handle assignments inside MAIN
        elif tok.type.upper() == "IDENT" and current_section == main_node:
            if (
                i + 2 < len(tokens)
                and tokens[i + 1].type.upper() == "ASSIGN"
                and tokens[i + 2].type.upper() == "NUMBER"
            ):
                if algo_node is None:
                    algo_node = ASTNode("ALGO")
                    main_node.add_child(algo_node)
                expr = f"{tok.value} = {tokens[i + 2].value}"
                algo_node.add_child(ASTNode("ASSIGN", value=expr))
                i += 2  # skip ahead

        # Handle print statements
        elif tok.type.upper() == "PRINT":
            if algo_node is None:
                algo_node = ASTNode("ALGO")
                main_node.add_child(algo_node)
            if i + 1 < len(tokens) and tokens[i + 1].type.upper() == "IDENT":
                algo_node.add_child(ASTNode("PRINT", value=tokens[i + 1].value))
                i += 1

        i += 1

    return program_node
