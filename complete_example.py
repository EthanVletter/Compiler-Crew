"""
Example integration showing how to use the complete SPL compiler pipeline:
Lexer -> Parser -> AST -> Symbol Table -> Code Generator

This demonstrates the full compilation process for SPL programs.
"""

from code_generator import generate_code_from_ast
from syntax_tree import ASTNode, ProgramNode, VarDeclNode
from symbol_table import SymbolTable


def create_sample_spl_program():
    """
    Create a sample SPL program AST equivalent to:
    
    var { x, y }
    main {
        x = 42;
        y = x + 8;
        print "The answer is: ";
        print y;
        halt;
    }
    """
    
    # Global variables: var { x, y }
    global_x = VarDeclNode("x")
    global_y = VarDeclNode("y")
    globals_node = ASTNode("GLOBALS", children=[global_x, global_y])
    
    # No procedures or functions
    procs_node = ASTNode("PROCS", children=[])
    funcs_node = ASTNode("FUNCS", children=[])
    
    # Main program algorithm
    # x = 42;
    assign1 = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="x"),
        ASTNode("NUMBER", value="42")
    ])
    
    # y = x + 8;
    add_expr = ASTNode("BINOP", children=[
        ASTNode("VAR", value="x"),
        ASTNode("OP", value="plus"),
        ASTNode("NUMBER", value="8")
    ])
    assign2 = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="y"),
        add_expr
    ])
    
    # print "The answer is: ";
    print1 = ASTNode("PRINT", children=[
        ASTNode("STRING", value="The answer is: ")
    ])
    
    # print y;
    print2 = ASTNode("PRINT", children=[
        ASTNode("VAR", value="y")
    ])
    
    # halt;
    halt = ASTNode("HALT")
    
    # Main algorithm
    algo = ASTNode("ALGO", children=[assign1, assign2, print1, print2, halt])
    
    # Main block (no local variables for this example)
    main_vars = ASTNode("VARIABLES", children=[])
    main_node = ASTNode("MAIN", children=[main_vars, algo])
    
    # Complete program
    program = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    
    return program


def create_symbol_table_for_sample():
    """Create appropriate symbol table for the sample program"""
    root = SymbolTable("everywhere")
    
    # Global scope with x and y
    global_scope = root.create_child_scope("global")
    global_scope.add("x", "var", node_id=1)
    global_scope.add("y", "var", node_id=2)
    
    return root


def compile_spl_program():
    """Complete compilation pipeline demonstration"""
    print("SPL Compiler Pipeline Demonstration")
    print("=" * 50)
    
    # Step 1: Create/Parse AST (normally this comes from your parser)
    print("Step 1: Building AST...")
    ast = create_sample_spl_program()
    
    # Step 2: Build Symbol Table (normally done during parsing)
    print("Step 2: Building Symbol Table...")
    symbol_table = create_symbol_table_for_sample()
    
    # Step 3: Display intermediate representations
    print("\nStep 3: Intermediate Representations")
    print("\n--- AST Structure ---")
    print(ast.pretty_print())
    
    print("\n--- Symbol Table ---")
    print(symbol_table.pretty_print())
    
    # Step 4: Generate Target Code
    print("\nStep 4: Code Generation")
    output_file = "compiled_output.txt"
    target_code = generate_code_from_ast(ast, symbol_table, output_file)
    
    print(f"\n✅ Compilation Complete!")
    print(f"📄 Target code saved to: {output_file}")
    print(f"\n📋 Generated Target Code:")
    print("-" * 30)
    print(target_code)
    print("-" * 30)
    
    return target_code


def create_complex_example():
    """Create a more complex example with conditionals and loops"""
    
    print("\n" + "=" * 60)
    print("COMPLEX EXAMPLE: SPL Program with Loops and Conditionals")
    print("=" * 60)
    
    # Program equivalent to:
    # var { max, i }  
    # main {
    #     max = 10;
    #     i = 1;
    #     while i <= max {
    #         if i > 5 {
    #             print "Large: ";
    #             print i;
    #         } else {
    #             print "Small: ";
    #             print i;
    #         }
    #         i = i + 1;
    #     }
    #     halt;
    # }
    
    # Globals
    globals_node = ASTNode("GLOBALS", children=[
        VarDeclNode("max"),
        VarDeclNode("i")
    ])
    
    procs_node = ASTNode("PROCS", children=[])
    funcs_node = ASTNode("FUNCS", children=[])
    
    # Main variables (none for this example)
    main_vars = ASTNode("VARIABLES", children=[])
    
    # max = 10;
    assign_max = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="max"),
        ASTNode("NUMBER", value="10")
    ])
    
    # i = 1;
    assign_i = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="i"),
        ASTNode("NUMBER", value="1")
    ])
    
    # Build the if-else inside loop
    # Condition: i > 5
    if_condition = ASTNode("BINOP", children=[
        ASTNode("VAR", value="i"),
        ASTNode("OP", value="gt"),
        ASTNode("NUMBER", value="5")
    ])
    
    # Then branch
    then_algo = ASTNode("ALGO", children=[
        ASTNode("PRINT", children=[ASTNode("STRING", value="Large: ")]),
        ASTNode("PRINT", children=[ASTNode("VAR", value="i")])
    ])
    
    # Else branch
    else_algo = ASTNode("ALGO", children=[
        ASTNode("PRINT", children=[ASTNode("STRING", value="Small: ")]),
        ASTNode("PRINT", children=[ASTNode("VAR", value="i")])
    ])
    
    if_stmt = ASTNode("IF", children=[if_condition, then_algo, else_algo])
    branch_node = ASTNode("BRANCH", children=[if_stmt])
    
    # i = i + 1;
    increment = ASTNode("BINOP", children=[
        ASTNode("VAR", value="i"),
        ASTNode("OP", value="plus"),
        ASTNode("NUMBER", value="1")
    ])
    update_i = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="i"),
        increment
    ])
    
    # Loop body
    loop_body = ASTNode("ALGO", children=[branch_node, update_i])
    
    # While condition: i <= max (using eq for simplicity)
    while_condition = ASTNode("BINOP", children=[
        ASTNode("VAR", value="i"),
        ASTNode("OP", value="eq"),  # Should be <= but using eq for demo
        ASTNode("VAR", value="max")
    ])
    
    while_node = ASTNode("WHILE", children=[while_condition, loop_body])
    loop_node = ASTNode("LOOP", children=[while_node])
    
    # halt
    halt = ASTNode("HALT")
    
    # Main algorithm
    main_algo = ASTNode("ALGO", children=[
        assign_max, assign_i, loop_node, halt
    ])
    
    main_node = ASTNode("MAIN", children=[main_vars, main_algo])
    program = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    
    # Symbol table
    symtab = SymbolTable("everywhere")
    global_scope = symtab.create_child_scope("global")
    global_scope.add("max", "var", node_id=1)
    global_scope.add("i", "var", node_id=2)
    
    # Generate code
    print("Generating complex program...")
    target_code = generate_code_from_ast(program, symtab, "complex_output.txt")
    
    return target_code


if __name__ == "__main__":
    # Run simple example
    compile_spl_program()
    
    # Run complex example
    create_complex_example()
    
    print("\n🎉 All examples completed successfully!")
    print("\nGenerated files:")
    print("  📄 compiled_output.txt - Simple arithmetic program")
    print("  📄 complex_output.txt - Complex program with loops and conditionals")
    print("\nYou can now examine these files to see the generated target code!")