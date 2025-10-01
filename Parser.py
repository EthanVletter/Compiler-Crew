from collections import defaultdict
from enum import Enum

# ========================
# Token and TokenType
# ========================
class TokenType(str, Enum):
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SEMI = ";"
    ASSIGN = "="
    GT = ">"
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Keywords
    GLOB = "glob"
    PROC = "proc"
    FUNC = "func"
    MAIN = "main"
    LOCAL = "local"
    VAR = "var"
    HALT = "halt"
    PRINT = "print"
    DO = "do"
    UNTIL = "until"
    WHILE = "while"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    NEG = "neg"
    NOT = "not"
    EQ = "eq"
    OR = "or"
    AND = "and"
    PLUS = "plus"
    MINUS = "minus"
    MULT = "mult"
    DIV = "div"
    
    EOF = "EOF"

class Token:
    def __init__(self, type_: TokenType, value: str, line: int = 1, col: int = 1):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

# ========================
# Parse Tree Node
# ========================
class ParseNode:
    def __init__(self, symbol, children=None):
        self.symbol = symbol
        self.children = children or []

    def __repr__(self, level=0):
        indent = "  " * level
        rep = f"{indent}{self.symbol}\n"
        for child in self.children:
            if isinstance(child, ParseNode):
                rep += child.__repr__(level + 1)
            else:
                rep += f"{indent}  {child}\n"
        return rep

# ========================
# Grammar and Item classes
# ========================
class Item:
    def __init__(self, head, body, dot=0):
        self.head = head
        self.body = body
        self.dot = dot
    def next_symbol(self):
        return self.body[self.dot] if self.dot < len(self.body) else None
    def is_complete(self):
        return self.dot == len(self.body)
    def __eq__(self, o): return (self.head, tuple(self.body), self.dot) == (o.head, tuple(o.body), o.dot)
    def __hash__(self): return hash((self.head, tuple(self.body), self.dot))
    def __repr__(self):
        b = self.body[:]
        b.insert(self.dot, "•")
        return f"{self.head} → {' '.join(b)}"

class Grammar:
    def __init__(self, start_symbol, productions):
        normalized = {}
        for head, bodies in productions.items():
            new_bodies = []
            for body in bodies:
                new_bodies.append([] if body == ["ε"] else body)
            normalized[head] = new_bodies
        self.start_symbol = start_symbol
        self.productions = normalized
        self.nonterminals = set(self.productions.keys())
        self.terminals = self._find_terminals()
    def _find_terminals(self):
        s = set()
        for bodies in self.productions.values():
            for body in bodies:
                for sym in body:
                    if sym not in self.productions and sym != "ε":
                        s.add(sym)
        return s

# ========================
# Helper functions (closure, goto, etc.)
# ========================
def closure(items, grammar):
    result = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for item in result:
            sym = item.next_symbol()
            if sym in grammar.nonterminals:
                for prod in grammar.productions[sym]:
                    new_items.add(Item(sym, prod, 0))
        if not new_items.issubset(result):
            result |= new_items
            changed = True
    return result

def goto(items, symbol, grammar):
    moved = {Item(i.head, i.body, i.dot + 1) for i in items if i.next_symbol() == symbol}
    return closure(moved, grammar) if moved else set()

def canonical_collection(grammar):
    start_item = Item(grammar.start_symbol, grammar.productions[grammar.start_symbol][0], 0)
    start_state = closure({start_item}, grammar)
    states = [start_state]
    transitions = {}
    changed = True
    while changed:
        changed = False
        for state in list(states):
            for sym in (grammar.terminals | grammar.nonterminals):
                new_state = goto(state, sym, grammar)
                if new_state:
                    if new_state not in states:
                        states.append(new_state)
                        changed = True
                    transitions[(states.index(state), sym)] = states.index(new_state)
    return states, transitions

def compute_first(grammar):
    first = defaultdict(set)
    for t in grammar.terminals:
        first[t].add(t)
    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.productions.items():
            for body in bodies:
                before = len(first[head])
                if not body:
                    first[head].add("ε")
                else:
                    nullable = True
                    for sym in body:
                        first[head] |= (first[sym] - {"ε"})
                        if "ε" not in first[sym]:
                            nullable = False
                            break
                    if nullable:
                        first[head].add("ε")
                if len(first[head]) > before:
                    changed = True
    return first

def compute_follow(grammar, first):
    follow = defaultdict(set)
    follow[grammar.start_symbol].add("$")
    changed = True
    while changed:
        changed = False
        for A, bodies in grammar.productions.items():
            for body in bodies:
                for i, B in enumerate(body):
                    if B in grammar.nonterminals:
                        beta = body[i+1:]
                        first_beta = set()
                        if not beta:
                            first_beta.add("ε")
                        else:
                            nullable = True
                            for sym in beta:
                                first_beta |= (first[sym] - {"ε"})
                                if "ε" not in first[sym]:
                                    nullable = False
                                    break
                            if nullable:
                                first_beta.add("ε")
                        before = len(follow[B])
                        follow[B] |= (first_beta - {"ε"})
                        if "ε" in first_beta:
                            follow[B] |= follow[A]
                        if len(follow[B]) > before:
                            changed = True
    return follow

def build_parsing_table(grammar, states, transitions, first, follow):
    action, goto_table, conflicts = {}, {}, []
    for i, state in enumerate(states):
        for sym in grammar.terminals:
            tgt = transitions.get((i, sym))
            if tgt is not None:
                action[(i, sym)] = ("shift", tgt)
        for item in state:
            if item.is_complete():
                if item.head == grammar.start_symbol:
                    action[(i, "$")] = ("accept", None)
                else:
                    for a in follow[item.head]:
                        if (i, a) in action and action[(i, a)][0] == "shift":
                            conflicts.append((i, a))
                            continue
                        action[(i, a)] = ("reduce", (item.head, item.body))
        for sym in grammar.nonterminals:
            tgt = transitions.get((i, sym))
            if tgt is not None:
                goto_table[(i, sym)] = tgt
    return action, goto_table

# ========================
# SLR Parser
# ========================
class SLRParser:
    def __init__(self, grammar, verbose=False):
        self.grammar = grammar
        self.verbose = verbose
        self.first = compute_first(grammar)
        self.follow = compute_follow(grammar, self.first)
        self.states, self.transitions = canonical_collection(grammar)
        self.action_table, self.goto_table = build_parsing_table(grammar, self.states, self.transitions, self.first, self.follow)

    def parse(self, tokens):
        stack = [0]
        node_stack = []
        pointer = 0

        while True:
            state = stack[-1]
            lookahead = tokens[pointer] if pointer < len(tokens) else "$"
            action = self.action_table.get((state, lookahead))
            if not action:
                if self.verbose:
                    print(f"Syntax error at token: {lookahead}")
                return None

            kind = action[0]
            if kind == "shift":
                stack.append(action[1])
                node_stack.append(ParseNode(lookahead))
                pointer += 1
            elif kind == "reduce":
                head, body = action[1]
                children = []
                for _ in body:
                    stack.pop()
                    children.insert(0, node_stack.pop())
                state = stack[-1]
                goto_state = self.goto_table.get((state, head))
                if goto_state is None:
                    return None
                stack.append(goto_state)
                node_stack.append(ParseNode(head, children))
            elif kind == "accept":
                return node_stack[0] if node_stack else None

    def parse_tokens(self, token_objects):
        token_strings = []
        for t in token_objects:
            if t.type in [TokenType.IDENT, TokenType.NUMBER, TokenType.STRING]:
                token_strings.append(t.type.value)
            else:
                token_strings.append(t.value)
        return self.parse(token_strings)

# ========================
# SPL Grammar Definition
# ========================
def build_spl_grammar():
    productions = {
        "S'": [["SPL_PROG"]],
        "SPL_PROG": [["glob","{","VARIABLES","}","proc","{","PROCDEFS","}","func","{","FUNCDEFS","}","main","{","MAINPROG","}"]],
        "VARIABLES": [[],["VAR","VARIABLES"]],
        "VAR": [["NAME"]],
        "NAME": [["IDENT"]],
        "PROCDEFS": [[],["PDEF","PROCDEFS"]],
        "PDEF": [["NAME","(","PARAM",")","{","BODY","}"]],
        "FUNCDEFS": [[],["FDEF","FUNCDEFS"]],
        "FDEF": [["NAME","(","PARAM",")","{","BODY",";","return","ATOM","}"]],
        "BODY": [["local","{","MAXTHREE","}","ALGO"]],
        "PARAM": [["MAXTHREE"]],
        "MAXTHREE": [[],["VAR"],["VAR","VAR"],["VAR","VAR","VAR"]],
        "MAINPROG": [["var","{","VARIABLES","}","ALGO"]],
        "ALGO": [["INSTR","INSTR_LIST"]],
        "INSTR_LIST": [[";","ALGO"],[]],
        "INSTR": [["halt"],["print","OUTPUT"],["ASSIGN"],["NAME","(","INPUT",")"],["LOOP"],["BRANCH"]],
        "ASSIGN": [["VAR","=","NAME","(","INPUT",")"],["VAR","=","TERM"]],
        "INPUT": [[],["ATOM"],["ATOM","ATOM"],["ATOM","ATOM","ATOM"]],
        "OUTPUT": [["ATOM"],["STRING"]],
        "ATOM": [["VAR"],["NUMBER"]],
        "TERM": [["ATOM"],["(","UNOP","TERM",")"],["(","TERM","BINOP","TERM",")"]],
        "UNOP": [["neg"],["not"]],
        "BINOP": [["eq"],[">"],["or"],["and"],["plus"],["minus"],["mult"],["div"]],
        "LOOP": [["while","TERM","{","ALGO","}"],["do","{","ALGO","}","until","TERM"]],
        "BRANCH": [["if","TERM","{","ALGO","}"],["if","TERM","{","ALGO","}","else","{","ALGO","}"]],
    }
    return Grammar("S'", productions)

def build_spl_parser(verbose=False):
    return SLRParser(build_spl_grammar(), verbose=verbose)