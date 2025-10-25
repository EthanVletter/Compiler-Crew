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


class ASTBuilder:
    """Comprehensive AST builder for SPL language"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def peek(self, offset=0):
        """Look ahead at tokens"""
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def advance(self):
        """Move to next token"""
        self.pos += 1
        self.current_token = (
            self.tokens[self.pos] if self.pos < len(self.tokens) else None
        )
        return self.current_token

    def match(self, expected_type):
        """Check if current token matches expected type"""
        if self.current_token and self.current_token.type == expected_type:
            token = self.current_token
            self.advance()
            return token
        return None

    def expect(self, expected_type):
        """Expect and consume a token of given type"""
        token = self.match(expected_type)
        if not token:
            raise ValueError(
                f"Expected {expected_type}, got {self.current_token.type if self.current_token else 'EOF'}"
            )
        return token

    def build(self):
        """Main entry point to build the complete AST"""
        return self.parse_program()

    def parse_program(self):
        """Parse: glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }"""

        # Parse globals
        self.expect("glob")
        self.expect("LBRACE")
        globals_node = self.parse_variables("GLOBALS")
        self.expect("RBRACE")

        # Parse procedures
        self.expect("proc")
        self.expect("LBRACE")
        procs_node = self.parse_procdefs()
        self.expect("RBRACE")

        # Parse functions
        self.expect("func")
        self.expect("LBRACE")
        funcs_node = self.parse_funcdefs()
        self.expect("RBRACE")

        # Parse main
        self.expect("main")
        self.expect("LBRACE")
        main_node = self.parse_mainprog()
        self.expect("RBRACE")

        return ProgramNode(
            globals_node=globals_node,
            procs_node=procs_node,
            funcs_node=funcs_node,
            main_node=main_node,
        )

    def parse_variables(self, node_type="VARS"):
        """Parse variable declarations"""
        vars_node = ASTNode(node_type)

        while self.current_token and self.current_token.type == "IDENT":
            var_name = self.current_token.value
            var_decl = VarDeclNode(var_name)
            vars_node.add_child(var_decl)
            self.advance()

        return vars_node

    def parse_procdefs(self):
        """Parse procedure definitions (placeholder - empty for now)"""
        return ASTNode("PROCS")

    def parse_funcdefs(self):
        """Parse function definitions (placeholder - empty for now)"""
        return ASTNode("FUNCS")

    def parse_mainprog(self):
        """Parse: var { VARIABLES } ALGO"""
        main_node = ASTNode("MAIN")

        # Parse local variables
        self.expect("var")
        self.expect("LBRACE")
        vars_node = self.parse_variables("VARS")
        self.expect("RBRACE")
        main_node.add_child(vars_node)

        # Parse algorithm
        algo_node = self.parse_algo()
        main_node.add_child(algo_node)

        return main_node

    def parse_algo(self):
        """Parse algorithm (sequence of instructions)"""
        algo_node = ASTNode("ALGO")

        # Parse first instruction
        instr = self.parse_instr()
        algo_node.add_child(instr)

        # Parse remaining instructions (INSTR ; ALGO)
        while self.current_token and self.current_token.type == "SEMI":
            self.advance()  # consume semicolon

            if self.current_token and self.current_token.type != "RBRACE":
                instr = self.parse_instr()
                algo_node.add_child(instr)

        return algo_node

    def parse_instr(self):
        """Parse individual instruction"""
        if not self.current_token:
            raise ValueError("Unexpected end of input")

        token_type = self.current_token.type

        if token_type == "halt":
            self.advance()
            return ASTNode("HALT")

        elif token_type == "print":
            return self.parse_print()

        elif token_type == "IDENT":
            return self.parse_assignment()

        elif token_type == "while":
            return self.parse_while_loop()

        elif token_type == "do":
            return self.parse_do_until_loop()

        elif token_type == "if":
            return self.parse_if_statement()

        else:
            raise ValueError(f"Unexpected token in instruction: {token_type}")

    def parse_print(self):
        """Parse: print OUTPUT"""
        self.expect("print")

        if self.current_token.type == "STRING":
            string_node = ASTNode("STRING", value=self.current_token.value)
            self.advance()
            return ASTNode("PRINT", children=[string_node])

        elif self.current_token.type == "IDENT":
            var_node = ASTNode("VAR", value=self.current_token.value)
            self.advance()
            return ASTNode("PRINT", children=[var_node])

        else:
            raise ValueError(
                f"Expected STRING or IDENT after print, got {self.current_token.type}"
            )

    def parse_assignment(self):
        """Parse: VAR = TERM"""
        var_name = self.current_token.value
        self.advance()

        self.expect("ASSIGN")

        term = self.parse_term()

        var_node = ASTNode("VAR", value=var_name)
        return ASTNode("ASSIGN", children=[var_node, term])

    def parse_term(self):
        """Parse TERM (ATOM, unary ops, binary ops)"""
        if self.current_token.type == "LPAREN":
            self.advance()  # consume (

            # Check for unary operation
            if self.current_token.type in ["neg", "not"]:
                op = self.current_token.value
                self.advance()

                operand = self.parse_term()
                self.expect("RPAREN")

                return ASTNode("UNOP", value=op, children=[operand])

            # Binary operation: ( TERM BINOP TERM )
            else:
                left = self.parse_term()

                if self.current_token.type in [
                    "eq",
                    "GT",
                    "or",
                    "and",
                    "plus",
                    "minus",
                    "mult",
                    "div",
                ]:
                    op = self.current_token.value
                    self.advance()

                    right = self.parse_term()
                    self.expect("RPAREN")

                    return ASTNode("BINOP", value=op, children=[left, right])
                else:
                    self.expect("RPAREN")
                    return left

        # Simple ATOM
        return self.parse_atom()

    def parse_atom(self):
        """Parse ATOM (VAR or number)"""
        if self.current_token.type == "IDENT":
            var_name = self.current_token.value
            self.advance()
            return ASTNode("VAR", value=var_name)

        elif self.current_token.type == "NUMBER":
            number = self.current_token.value
            self.advance()
            return ASTNode("NUMBER", value=number)

        else:
            raise ValueError(f"Expected IDENT or NUMBER, got {self.current_token.type}")

    def parse_while_loop(self):
        """Parse: while TERM { ALGO }"""
        self.expect("while")

        condition = self.parse_term()

        self.expect("LBRACE")
        body = self.parse_algo()
        self.expect("RBRACE")

        while_node = ASTNode("WHILE", children=[condition, body])
        return ASTNode("LOOP", children=[while_node])

    def parse_do_until_loop(self):
        """Parse: do { ALGO } until TERM"""
        self.expect("do")
        self.expect("LBRACE")

        body = self.parse_algo()

        self.expect("RBRACE")
        self.expect("until")

        condition = self.parse_term()

        do_node = ASTNode("DO", children=[body, condition])
        return ASTNode("LOOP", children=[do_node])

    def parse_if_statement(self):
        """Parse: if TERM { ALGO } [else { ALGO }]"""
        self.expect("if")

        condition = self.parse_term()

        self.expect("LBRACE")
        then_body = self.parse_algo()
        self.expect("RBRACE")

        if self.current_token and self.current_token.type == "else":
            self.advance()  # consume else
            self.expect("LBRACE")
            else_body = self.parse_algo()
            self.expect("RBRACE")

            if_node = ASTNode("IF", children=[condition, then_body, else_body])
        else:
            if_node = ASTNode("IF", children=[condition, then_body])

        return ASTNode("BRANCH", children=[if_node])


def build_ast(tokens):
    """Builds and populates a complete AST from the given token list."""

    # Initialize the AST builder
    builder = ASTBuilder(tokens)
    return builder.build()
