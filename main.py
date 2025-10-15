# main.py

from lexer import Lexer, LexerError, TokenType
from parser import build_spl_grammar, SLRParser, Token, TokenType
from syntax_tree import ProgramNode, VarDeclNode, ASTNode
from symbol_table import SymbolTable
from code_generator import generate_code_from_ast
from basic_converter import convert_intermediate_to_basic

# from type_checker import TypeChecker

import sys


def compile_spl_from_file(input_file, output_bas):
    """Full SPL pipeline reading input from a file."""

    # Step 1: Read source SPL code from file
    with open(input_file, "r") as f:
        source_code = f.read()

    print("=" * 60)
    print("SPL Compiler Pipeline Demonstration (File Input)")
    print("=" * 60)

    # Step 2: Lexical Analysis
    print("Step 1: Lexical Analysis")
    # lexer = Lexer(source_code)
    # tokens = lexer.tokenize()
    # print(f"Tokens: {tokens}")

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

    # Step 3: Parsing
    print("Step 2: Parsing")
    parser = SLRParser(tokens)
    ast = parser.parse()
    print("AST generated.")

    # Step 4: Build Syntax Tree
    #
    #
    #
    #
    #

    # Step 5: Build Symbol Table
    print("Step 3: Building Symbol Table")
    # Using your helper method from the file you provided
    symbol_table = SymbolTable("everywhere")
    # Populate symbol table from AST
    symbol_table.populate_from_ast(ast)
    print(symbol_table.pretty_print())

    # Step 6: Type Checking
    #
    #
    #
    #
    #
    #

    # Step 7: Code Generation
    print("Step 4: Code Generation")
    intermediate_file = "intermediate_output.txt"
    target_code = generate_code_from_ast(ast, symbol_table, intermediate_file)
    print(f"Intermediate code written to {intermediate_file}")

    # Step 8: Convert to line-numbered BASIC
    print("Step 5: Converting to line-numbered BASIC")
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
