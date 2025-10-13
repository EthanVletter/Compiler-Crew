"""
Test file for the SPL Code Generator
This demonstrates how to use the code generator and creates test programs
"""

from syntax_tree import ASTNode, ProgramNode, VarDeclNode, FuncNode, ProcNode
from symbol_table import SymbolTable
from code_generator import generate_code_from_ast


def build_simple_test_ast():
    """Build a simple test AST: main program with basic operations"""
    
    # Global variables
    global_x = VarDeclNode("x")
    global_y = VarDeclNode("y")
    globals_node = ASTNode("GLOBALS", children=[global_x, global_y])
    
    # No procedures or functions for this test
    procs_node = ASTNode("PROCS", children=[])
    funcs_node = ASTNode("FUNCS", children=[])
    
    # Main program variables
    main_vars = ASTNode("VARIABLES", children=[
        VarDeclNode("result"),
        VarDeclNode("temp")
    ])
    
    # Build the main algorithm
    # result = 10 + 5;
    num1 = ASTNode("NUMBER", value="10")
    num2 = ASTNode("NUMBER", value="5")
    plus_op = ASTNode("BINOP", children=[
        num1,
        ASTNode("OP", value="plus"),
        num2
    ])
    result_var = ASTNode("VAR", value="result")
    assign1 = ASTNode("ASSIGN", children=[result_var, plus_op])
    
    # print "Result is: ";
    print_str = ASTNode("PRINT", children=[
        ASTNode("STRING", value="Result is: ")
    ])
    
    # print result;
    print_result = ASTNode("PRINT", children=[
        ASTNode("VAR", value="result")
    ])
    
    # temp = result * 2;
    mult_op = ASTNode("BINOP", children=[
        ASTNode("VAR", value="result"),
        ASTNode("OP", value="mult"),
        ASTNode("NUMBER", value="2")
    ])
    temp_var = ASTNode("VAR", value="temp")
    assign2 = ASTNode("ASSIGN", children=[temp_var, mult_op])
    
    # print temp;
    print_temp = ASTNode("PRINT", children=[
        ASTNode("VAR", value="temp")
    ])
    
    # halt;
    halt_instr = ASTNode("HALT")
    
    # Build ALGO node
    algo_node = ASTNode("ALGO", children=[
        assign1, print_str, print_result, assign2, print_temp, halt_instr
    ])
    
    # Main program node
    main_node = ASTNode("MAIN", children=[main_vars, algo_node])
    
    # Complete program
    program = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    
    return program


def build_conditional_test_ast():
    """Build a test AST with conditional (if-else) statements"""
    
    # Global variables
    globals_node = ASTNode("GLOBALS", children=[VarDeclNode("globalVar")])
    procs_node = ASTNode("PROCS", children=[])
    funcs_node = ASTNode("FUNCS", children=[])
    
    # Main variables
    main_vars = ASTNode("VARIABLES", children=[
        VarDeclNode("x"),
        VarDeclNode("y")
    ])
    
    # x = 15;
    assign_x = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="x"),
        ASTNode("NUMBER", value="15")
    ])
    
    # y = 10;
    assign_y = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="y"),
        ASTNode("NUMBER", value="10")
    ])
    
    # if x > y { print "x is larger"; } else { print "y is larger"; }
    condition = ASTNode("BINOP", children=[
        ASTNode("VAR", value="x"),
        ASTNode("OP", value="gt"),
        ASTNode("VAR", value="y")
    ])
    
    then_algo = ASTNode("ALGO", children=[
        ASTNode("PRINT", children=[ASTNode("STRING", value="x is larger")])
    ])
    
    else_algo = ASTNode("ALGO", children=[
        ASTNode("PRINT", children=[ASTNode("STRING", value="y is larger")])
    ])
    
    if_node = ASTNode("IF", children=[condition, then_algo, else_algo])
    branch_node = ASTNode("BRANCH", children=[if_node])
    
    # halt;
    halt_instr = ASTNode("HALT")
    
    # Main algorithm
    algo_node = ASTNode("ALGO", children=[
        assign_x, assign_y, branch_node, halt_instr
    ])
    
    main_node = ASTNode("MAIN", children=[main_vars, algo_node])
    program = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    
    return program


def build_loop_test_ast():
    """Build a test AST with loops"""
    
    globals_node = ASTNode("GLOBALS", children=[])
    procs_node = ASTNode("PROCS", children=[])
    funcs_node = ASTNode("FUNCS", children=[])
    
    # Main variables
    main_vars = ASTNode("VARIABLES", children=[
        VarDeclNode("counter"),
        VarDeclNode("limit")
    ])
    
    # counter = 1;
    init_counter = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="counter"),
        ASTNode("NUMBER", value="1")
    ])
    
    # limit = 5;
    init_limit = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="limit"),
        ASTNode("NUMBER", value="5")
    ])
    
    # while counter <= limit { print counter; counter = counter + 1; }
    while_condition = ASTNode("BINOP", children=[
        ASTNode("VAR", value="counter"),
        ASTNode("OP", value="eq"),  # Using eq for simplicity (should be <=)
        ASTNode("VAR", value="limit")
    ])
    
    # Loop body: print counter; counter = counter + 1;
    print_counter = ASTNode("PRINT", children=[ASTNode("VAR", value="counter")])
    
    increment = ASTNode("BINOP", children=[
        ASTNode("VAR", value="counter"),
        ASTNode("OP", value="plus"),
        ASTNode("NUMBER", value="1")
    ])
    
    update_counter = ASTNode("ASSIGN", children=[
        ASTNode("VAR", value="counter"),
        increment
    ])
    
    loop_body = ASTNode("ALGO", children=[print_counter, update_counter])
    
    while_node = ASTNode("WHILE", children=[while_condition, loop_body])
    loop_node = ASTNode("LOOP", children=[while_node])
    
    # halt;
    halt_instr = ASTNode("HALT")
    
    # Main algorithm
    algo_node = ASTNode("ALGO", children=[
        init_counter, init_limit, loop_node, halt_instr
    ])
    
    main_node = ASTNode("MAIN", children=[main_vars, algo_node])
    program = ProgramNode(globals_node, procs_node, funcs_node, main_node)
    
    return program


def build_symbol_table_for_simple_test():
    """Build symbol table for the simple test"""
    root = SymbolTable("everywhere")
    
    # Global scope
    global_scope = root.create_child_scope("global")
    global_scope.add("x", "var", node_id=1)
    global_scope.add("y", "var", node_id=2)
    
    # Main scope  
    main_scope = root.create_child_scope("main")
    main_scope.add("result", "var", node_id=3)
    main_scope.add("temp", "var", node_id=4)
    
    return root


def build_symbol_table_for_conditional_test():
    """Build symbol table for conditional test"""
    root = SymbolTable("everywhere")
    
    global_scope = root.create_child_scope("global")
    global_scope.add("globalVar", "var", node_id=1)
    
    main_scope = root.create_child_scope("main")
    main_scope.add("x", "var", node_id=2)
    main_scope.add("y", "var", node_id=3)
    
    return root


def build_symbol_table_for_loop_test():
    """Build symbol table for loop test"""
    root = SymbolTable("everywhere")
    
    main_scope = root.create_child_scope("main")
    main_scope.add("counter", "var", node_id=1)
    main_scope.add("limit", "var", node_id=2)
    
    return root


def run_test(test_name, ast, symbol_table, output_file):
    """Run a single test case"""
    print(f"\n{'='*50}")
    print(f"Running {test_name}")
    print(f"{'='*50}")
    
    print("\n--- AST Structure ---")
    print(ast.pretty_print())
    
    print("\n--- Symbol Table ---")
    print(symbol_table.pretty_print())
    
    print(f"\n--- Generating Code to {output_file} ---")
    target_code = generate_code_from_ast(ast, symbol_table, output_file)
    
    return target_code


def main():
    """Run all tests"""
    print("SPL Code Generator Test Suite")
    print("=" * 60)
    
    # Test 1: Simple arithmetic and assignment
    print("\nTest 1: Simple Arithmetic Operations")
    ast1 = build_simple_test_ast()
    symtab1 = build_symbol_table_for_simple_test()
    code1 = run_test("Simple Arithmetic Test", ast1, symtab1, "simple_test_output.txt")
    
    # Test 2: Conditional statements
    print("\nTest 2: Conditional Statements (if-else)")
    ast2 = build_conditional_test_ast()
    symtab2 = build_symbol_table_for_conditional_test()
    code2 = run_test("Conditional Test", ast2, symtab2, "conditional_test_output.txt")
    
    # Test 3: Loop statements
    print("\nTest 3: Loop Statements (while)")
    ast3 = build_loop_test_ast()
    symtab3 = build_symbol_table_for_loop_test()
    code3 = run_test("Loop Test", ast3, symtab3, "loop_test_output.txt")
    
    print(f"\n{'='*60}")
    print("All tests completed!")
    print("Generated files:")
    print("  - simple_test_output.txt")
    print("  - conditional_test_output.txt") 
    print("  - loop_test_output.txt")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()