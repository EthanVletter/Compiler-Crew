class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.temp_counter = 0
        self.label_counter = 0
        
    def new_temp(self):
        """Generate a new temporary variable"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self):
        """Generate a new label"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def generate(self, ast_root):
        """Main entry point for code generation"""
        code = []
        
        # Generate code for the main program
        main_node = self._find_main_node(ast_root)
        if main_node:
            code.extend(self._translate_main(main_node))
        
        return "\n".join(code)
    
    def _find_main_node(self, program_node):
        """Find the main node in the program AST"""
        # ProgramNode has children: [globals, procs, funcs, main]
        if hasattr(program_node, 'children') and len(program_node.children) >= 4:
            return program_node.children[3]  # main is the 4th child
        
        # Fallback: search for MAIN type
        for child in program_node.children:
            if child.type == "MAIN":
                return child
        return None
    
    def _translate_main(self, main_node):
        """Translate main program - only ALGO part, skip variable declarations"""
        code = []
        
        # Find ALGO node (skip VAR declarations)
        for child in main_node.children:
            if child.type == "ALGO":
                code.extend(self._translate_algo(child))
        
        return code
    
    def _translate_algo(self, algo_node):
        """Translate ALGO ::= INSTR ; ALGO"""
        code = []
        
        for child in algo_node.children:
            if child.type in ["ASSIGN", "PRINT", "HALT", "BRANCH", "LOOP", "CALL"]:
                code.extend(self._translate_instr(child))
        
        return code
    
    def _translate_instr(self, instr_node):
        """Translate individual instructions"""
        if instr_node.type == "HALT":
            return ["STOP"]
        
        elif instr_node.type == "PRINT":
            return self._translate_print(instr_node)
        
        elif instr_node.type == "ASSIGN":
            return self._translate_assign(instr_node)
        
        elif instr_node.type == "BRANCH":
            return self._translate_branch(instr_node)
        
        elif instr_node.type == "LOOP":
            return self._translate_loop(instr_node)
        
        elif instr_node.type == "CALL":
            return self._translate_call(instr_node)
        
        return []
    
    def _translate_print(self, print_node):
        """Translate print OUTPUT"""
        code = []
        
        # Get the output node
        output_node = print_node.children[0] if print_node.children else None
        
        if output_node:
            if output_node.type == "STRING":
                code.append(f'PRINT "{output_node.value}"')
            
            elif output_node.type == "NUMBER":
                code.append(f"PRINT {output_node.value}")
            
            elif output_node.type == "VAR":
                # Look up variable in symbol table
                symbol = self.symbol_table.lookup(output_node.value)
                if symbol:
                    internal_name = f"{symbol.scope}_{symbol.name}"
                    code.append(f"PRINT {internal_name}")
                else:
                    code.append(f"PRINT {output_node.value}")
        
        return code
    
    def _translate_assign(self, assign_node):
        """Translate VAR = TERM"""
        code = []
        
        if len(assign_node.children) >= 2:
            var_node = assign_node.children[0]  # VAR
            term_node = assign_node.children[1]  # TERM
            
            # Generate code for the term
            term_code, term_result = self._translate_term(term_node)
            code.extend(term_code)
            
            # Look up variable in symbol table
            symbol = self.symbol_table.lookup(var_node.value)
            if symbol:
                internal_name = f"{symbol.scope}_{symbol.name}"
                code.append(f"{internal_name} = {term_result}")
            else:
                # Fallback if symbol not found
                code.append(f"{var_node.value} = {term_result}")
        
        return code
    
    def _translate_term(self, term_node):
        """Translate TERM - returns (code_list, result_var)"""
        code = []
        
        if term_node.type == "VAR":
            # ATOM ::= VAR
            symbol = self.symbol_table.lookup(term_node.value)
            if symbol:
                internal_name = f"{symbol.scope}_{symbol.name}"
                return code, internal_name
            return code, term_node.value
        
        elif term_node.type == "NUMBER":
            # ATOM ::= number
            return code, str(term_node.value)
        
        elif term_node.type == "UNOP":
            # ( UNOP TERM )
            if len(term_node.children) >= 2:
                op_node = term_node.children[0]
                operand_node = term_node.children[1]
                
                operand_code, operand_result = self._translate_term(operand_node)
                code.extend(operand_code)
                
                temp = self.new_temp()
                
                if op_node.value == "neg":
                    code.append(f"{temp} = -{operand_result}")
                elif op_node.value == "not":
                    # Handle NOT separately in conditional contexts
                    code.append(f"{temp} = !{operand_result}")
                
                return code, temp
        
        elif term_node.type == "BINOP":
            # ( TERM BINOP TERM )
            if len(term_node.children) >= 3:
                left_node = term_node.children[0]
                op_node = term_node.children[1]
                right_node = term_node.children[2]
                
                left_code, left_result = self._translate_term(left_node)
                code.extend(left_code)
                
                right_code, right_result = self._translate_term(right_node)
                code.extend(right_code)
                
                temp = self.new_temp()
                # Handle the case where op_node might be an OP node with value
                op_symbol = self._get_binop_symbol(op_node.value if hasattr(op_node, 'value') else op_node.type)
                
                code.append(f"{temp} = {left_result} {op_symbol} {right_result}")
                return code, temp
        
        return code, "0"  # fallback
    
    def _get_binop_symbol(self, op_name):
        """Convert SPL binary operators to target symbols"""
        op_map = {
            "plus": "+",
            "minus": "-", 
            "mult": "*",
            "div": "/",
            "eq": "=",
            "gt": ">"
        }
        return op_map.get(op_name, op_name)
    
    def _translate_branch(self, branch_node):
        """Translate if statements"""
        code = []
        
        if branch_node.children and branch_node.children[0].type == "IF":
            if_node = branch_node.children[0]
            
            # Get condition, then_algo, and possibly else_algo
            condition_node = if_node.children[0] if len(if_node.children) > 0 else None
            then_algo = if_node.children[1] if len(if_node.children) > 1 else None
            else_algo = if_node.children[2] if len(if_node.children) > 2 else None
            
            # Generate labels
            label_true = self.new_label()
            label_exit = self.new_label()
            
            # Generate condition code
            cond_code, cond_result = self._translate_term(condition_node)
            code.extend(cond_code)
            
            if else_algo:
                # if-else form
                code.append(f"IF {cond_result} = 1 THEN {label_true}")
                
                # else part
                code.extend(self._translate_algo(else_algo))
                code.append(f"GOTO {label_exit}")
                
                # then part
                code.append(f"REM {label_true}")
                code.extend(self._translate_algo(then_algo))
                code.append(f"REM {label_exit}")
            
            else:
                # if-only form
                code.append(f"IF {cond_result} = 1 THEN {label_true}")
                code.append(f"GOTO {label_exit}")
                
                # then part
                code.append(f"REM {label_true}")
                code.extend(self._translate_algo(then_algo))
                code.append(f"REM {label_exit}")
        
        return code
    
    def _translate_loop(self, loop_node):
        """Translate while and do-until loops"""
        code = []
        
        if loop_node.children:
            loop_type = loop_node.children[0].type
            
            if loop_type == "WHILE":
                # while TERM { ALGO }
                while_node = loop_node.children[0]
                condition_node = while_node.children[0]
                body_algo = while_node.children[1]
                
                label_start = self.new_label()
                label_body = self.new_label() 
                label_exit = self.new_label()
                
                code.append(f"REM {label_start}")
                
                # Generate condition
                cond_code, cond_result = self._translate_term(condition_node)
                code.extend(cond_code)
                
                code.append(f"IF {cond_result} = 1 THEN {label_body}")
                code.append(f"GOTO {label_exit}")
                
                code.append(f"REM {label_body}")
                code.extend(self._translate_algo(body_algo))
                code.append(f"GOTO {label_start}")
                
                code.append(f"REM {label_exit}")
            
            elif loop_type == "DO":
                # do { ALGO } until TERM
                do_node = loop_node.children[0]
                body_algo = do_node.children[0]
                condition_node = do_node.children[1]
                
                label_start = self.new_label()
                label_exit = self.new_label()
                
                code.append(f"REM {label_start}")
                code.extend(self._translate_algo(body_algo))
                
                # Generate condition 
                cond_code, cond_result = self._translate_term(condition_node)
                code.extend(cond_code)
                
                code.append(f"IF {cond_result} = 1 THEN {label_exit}")
                code.append(f"GOTO {label_start}")
                code.append(f"REM {label_exit}")
        
        return code
    
    def _translate_call(self, call_node):
        """Translate procedure/function calls - placeholder for inlining"""
        code = []
        
        if call_node.children:
            name_node = call_node.children[0]
            # For now, generate a CALL instruction
            # Later this will be replaced by inlining
            code.append(f"CALL {name_node.value}")
        
        return code

def generate_code_from_ast(ast_root, symbol_table, output_file="output.txt"):
    """Main function to generate code and save to file"""
    generator = CodeGenerator(symbol_table)
    target_code = generator.generate(ast_root)
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.write(target_code)
    
    print(f"Code generation complete. Output saved to {output_file}")
    print("\nGenerated code:")
    print(target_code)
    
    return target_code