# Compiler-Crew

# COS341 - SPL Compiler

## Overview

This project is a **compiler for the SPL (Simple Programming Language)**, developed as part of the COS 341 course.  
The compiler performs all main compilation stages:

- **Lexical Analysis**
- **Parsing**
- **Abstract Syntax Tree (AST) Generation**
- **Symbol Table construction**
- **Type Checking**
- **Intermediate Code Generation**
- **Conversion to BASIC Code**.

## Team Members

| Name            | Student Number |
| --------------- | -------------- |
| Ethan Vletter   | u22497082      |
| Nthati Rampa    | u20475102      |
| Thuwayba Dawood | u22622668      |
| Nobuhle Mtshali | u22526171      |

## 📂 Project Structure

```bash
📁 Compiler-Crew
├── 📜 main.py
├── 📜 lexer.py
├── 📜 parser.py
├── 📜 syntax_tree.py
├── 📜 symbol_table.py
├── 📜 type_checker.py
├── 📜 code_generator.py
├── 📜 basic_converter.py
├── 📜 utils.py
├── 📄 input.txt
├── 📄 output.bas
└── 📘 README.md
```

## How to Run

### **Requirements**

- Python **3.10+**
- All source files in the same directory (as shown above)

---

### **Run the Compiler**

Run this command in your terminal:

```bash
python main.py <input_file.txt> <output_file.bas>
```

Example:

```bash
python main.py input.txt output.bas
```

### **Input / Output**

Example SPL Input

```bash
glob { }
proc { }
func { }
main {
var { x }
x = 42;
print x
}
```

Generated BASIC Output

```bash
10 x = 42
20 PRINT x
30 STOP
```

Or for a more complex input:

```bash
glob { }
proc { }
func { }
main {
var { x, y }
x = 42;
y = x + 8;
print "The answer is: ";
print y;
}
```

Output:

```bash
10 x = 42
20 t1 = x + 8
30 y = t1
40 PRINT "The answer is: "
50 PRINT y
60 STOP
```

### Expected Input / Output Summary

| Stage                | Input              | Output            | Description                                                              |
| -------------------- | ------------------ | ----------------- | ------------------------------------------------------------------------ |
| Lexical Analysis     | SPL source         | Tokens            | Converts SPL code into token stream                                      |
| Parsing              | Tokens             | Parse Tree / AST  | Validates syntax and constructs the program’s structural representation. |
| Abstract Syntax Tree | Parsed structure   | Hierarchical AST  | Builds Abstract Syntax Tree                                              |
| Symbol Table         | AST                | Table             | Tracks variable/function definitions                                     |
| Type Checker         | AST + Symbol Table | Report            | Ensures consistent data types                                            |
| Code Generator       | AST + Symbol Table | Intermediate code | Produces simplified machine-like code                                    |
| BASIC Converter      | Intermediate code  | `.bas` file       | Translates into numbered BASIC code                                      |
