from syntax_tree import ASTNode, ProgramNode, VarDeclNode
from symbol_table import SymbolTable

# ---------------- Symbol Table Demo ----------------
root = SymbolTable("everywhere")

globals_scope = root.create_child_scope("global")
globals_scope.add("x", "var")
globals_scope.add("y", "var")

func_scope = root.create_child_scope("function myFunc")
func_scope.add("myFunc", "func", extra={"params": ["a"], "return": "int"})
func_scope.add("a", "var")
func_scope.add("temp", "var")

proc_scope = root.create_child_scope("procedure myProc")
proc_scope.add("myProc", "proc", extra={"params": ["p1"]})
proc_scope.add("p1", "var")
proc_scope.add("localVar", "var")

print("=== SYMBOL TABLE ===")
print(root)

# ---------------- AST Demo ----------------
var_x = VarDeclNode("x")
var_y = VarDeclNode("y")
globals_node = ASTNode("GLOBALS", children=[var_x, var_y])
main_node = ASTNode("MAIN")
prog = ProgramNode(
    globals_node,
    procs_node=ASTNode("PROCS"),
    funcs_node=ASTNode("FUNCS"),
    main_node=main_node,
)

print("\n=== SYNTAX TREE ===")
print(prog.pretty_print())
