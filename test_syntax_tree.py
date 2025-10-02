from parser import build_spl_grammar, SLRParser, Token, TokenType
from syntax_tree import ProgramNode, VarDeclNode, ASTNode
from symbol_table import SymbolTable


def build_mock_ast():
    """For now, construct a small AST manually (later connect during parsing)."""
    # global vars
    global_x = VarDeclNode("globalVar")
    globals_node = ASTNode("GLOBALS", children=[global_x])

    # main vars
    local_var = VarDeclNode("localVar")
    main_vars = ASTNode("VARS", children=[local_var])

    # main algorithm
    assign = ASTNode("ASSIGN", value="localVar = 42")
    prnt = ASTNode("PRINT", value="localVar")
    algo = ASTNode("ALGO", children=[assign, prnt])

    main_node = ASTNode("MAIN", children=[main_vars, algo])

    # program root
    prog = ProgramNode(
        globals_node,
        procs_node=ASTNode("PROCS"),
        funcs_node=ASTNode("FUNCS"),
        main_node=main_node,
    )

    return prog


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


def test_parser_and_ast():
    grammar = build_spl_grammar()
    parser = SLRParser(grammar)

    # Tokens for: glob { globalVar } proc { } func { } main { var { localVar } localVar = 42; print localVar }
    tokens = [
        Token(TokenType.GLOB, "glob"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.IDENT, "globalVar"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.PROC, "proc"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.FUNC, "func"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.MAIN, "main"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.VAR, "var"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.IDENT, "localVar"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.IDENT, "localVar"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.NUMBER, "42"),
        Token(TokenType.SEMI, ";"),
        Token(TokenType.PRINT, "print"),
        Token(TokenType.IDENT, "localVar"),
        Token(TokenType.RBRACE, "}"),
    ]

    # Show the program as readable SPL source
    print("=== INPUT PROGRAM ===")
    program_text = """
    glob { globalVar }
    proc { }
    func { }
    main {
        var { localVar }
        localVar = 42;
        print localVar
    }
    """.strip()
    print(program_text)

    print("\n=== PARSER CHECK ===")
    ok = parser.parse_tokens(tokens)
    print("Parse result:", ok)

    print("\n=== AST ===")
    ast = build_mock_ast()
    print(ast.pretty_print())

    print("\n=== SYMBOL TABLE ===")
    symtab = build_symbol_table(ast)
    print(symtab.pretty_print())


if __name__ == "__main__":
    test_parser_and_ast()
