# main.py

from lexer import Lexer, LexerError, TokenType
from parser import build_spl_grammar, SLRParser, Token, TokenType
from syntax_tree import ProgramNode, VarDeclNode, ASTNode, build_ast
from symbol_table import SymbolTable, build_symbol_table
from type_checker import TypeChecker
from code_generator import generate_code_from_ast
from basic_converter import convert_intermediate_to_basic

import sys


def convert_lexer_token_to_parser_string(token):
    """Convert a lexer Token to a string the parser expects"""
    # For identifiers, numbers, and strings, use the token type name
    if token.type == "IDENT":
        return "IDENT"
    elif token.type == "NUMBER":
        return "NUMBER"
    elif token.type == "STRING":
        return "STRING"
    else:
        # For keywords and symbols, use the actual token value
        return token.value


def compile_spl_from_file(input_file, output_bas):
    """Full SPL pipeline reading input from a file."""

    # ---------------------------------------------------------------------------- #

    # Step 0: Read source SPL code from file
    print("\n" + "-" * 60)
    print("Step 0: Read source SPL code from file")
    print("-" * 60)

    with open(input_file, "r") as file:
        source_code = file.read()
        print(source_code)

    print("=" * 60)
    print("SPL Compiler Pipeline Demonstration (File Input)")
    print("=" * 60)

    # ---------------------------------------------------------------------------- #

    # Step 1: Lexical Analysis
    print("\n" + "-" * 60)
    print("Step 1: Lexical Analysis")
    print("-" * 60)

    # Tokenize
    try:
        lexer = Lexer(source_code)
        tokens = list(lexer)
        print(f"\n✅ Lexing successful - {len(tokens)} tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i:2d}: {token}")
    except LexerError as e:
        print(f"❌ Lexer error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected lexer error: {e}")
        return False

    # ---------------------------------------------------------------------------- #

    # Step 2: Parsing
    print("\n" + "-" * 60)
    print("Step 2: Parsing")
    print("-" * 60)

    # Convert to parser format
    parser_tokens = [convert_lexer_token_to_parser_string(token) for token in tokens]
    print(f"\nConverted tokens for parser: {parser_tokens}")

    # Parse
    try:
        grammar = build_spl_grammar()
        parser = SLRParser(grammar)
        print(f"\n🔄 Starting parse...")

        result = parser.parse(parser_tokens)
        print(f"Parse result: {'✅ SUCCESS' if result else '❌ FAILED'}")

        if result == False:
            return
        # return result

    except Exception as e:
        print(f"❌ Parser error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # ---------------------------------------------------------------------------- #

    # Step 3: Build Syntax Tree
    print("\n" + "-" * 60)
    print("Step 3: Build Syntax Tree")
    print("-" * 60)
    # ast = build_mock_ast()
    # ast = build_ast()
    ast = build_ast(tokens)
    print(ast.pretty_print())

    # print("\n=== SYMBOL TABLE ===")
    # symtab = build_symbol_table(ast)
    # print(symtab.pretty_print())
    #

    # ---------------------------------------------------------------------------- #

    # Step 4: Build Symbol Table
    print("\n" + "-" * 60)
    print("Step 4: Building Symbol Table")
    print("-" * 60)
    # Using your helper method from the file you provided
    # symbol_table = SymbolTable("everywhere")
    symbol_table = build_symbol_table(ast)
    # Populate symbol table from AST
    # symbol_table.populate_from_ast(ast)
    print(symbol_table.pretty_print())

    # ---------------------------------------------------------------------------- #

    # Step 5: Type Checking
    print("\n" + "-" * 60)
    print("Step 5: Type Checking")
    print("-" * 60)
    #
    checker = TypeChecker(symbol_table)
    report = checker.check_program(ast)
    # print(report)

    # Check if report has messages
    if hasattr(report, "messages"):
        if len(report.messages) == 0:
            print("✅ Type checking passed with no errors.")
        else:
            print("⚠️ Type checking report:")
            for msg in report.messages:
                print("  -", msg)
    else:
        # Fallback if report is just a list or string
        print(report)

    # ---------------------------------------------------------------------------- #

    # Step 6: Code Generation
    print("\n" + "-" * 60)
    print("Step 6: Code Generation")
    print("-" * 60)
    intermediate_file = "intermediate_output.txt"
    target_code = generate_code_from_ast(ast, symbol_table, intermediate_file)
    print(f"Intermediate code written to {intermediate_file}")

    print(f"\n📋 Generated Target Code:")
    print("-" * 30)
    print(target_code)
    print("-" * 30)

    # ---------------------------------------------------------------------------- #

    # Step 7: Convert to line-numbered BASIC
    print("\n" + "-" * 60)
    print("Step 7: Converting to line-numbered BASIC")
    print("-" * 60)
    convert_intermediate_to_basic(intermediate_file, output_bas)
    print(f"Executable BASIC code written to {output_bas}")

    print("\n✅ Compilation Complete!")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.txt> <output.bas>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_bas = sys.argv[2]

    compile_spl_from_file(input_file, output_bas)
