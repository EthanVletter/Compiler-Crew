from collections import defaultdict
from enum import Enum


# ========================
# Lexer Classes (simplified version)
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
# Grammar and Parser Classes (from previous artifact)
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

    def __eq__(self, other):
        return (self.head, tuple(self.body), self.dot) == (
            other.head,
            tuple(other.body),
            other.dot,
        )

    def __hash__(self):
        return hash((self.head, tuple(self.body), self.dot))

    def __repr__(self):
        body = self.body[:]
        body.insert(self.dot, "•")
        return f"{self.head} → {' '.join(body)}"


class Grammar:
    def __init__(self, start_symbol, productions):
        normalized = {}
        for head, bodies in productions.items():
            new_bodies = []
            for body in bodies:
                if body == ["ε"]:
                    new_bodies.append([])
                else:
                    new_bodies.append(body)
            normalized[head] = new_bodies

        self.start_symbol = start_symbol
        self.productions = normalized
        self.nonterminals = set(self.productions.keys())
        self.terminals = self._find_terminals()

    def _find_terminals(self):
        symbols = set()
        for bodies in self.productions.values():
            for body in bodies:
                for sym in body:
                    if sym not in self.productions and sym != "ε":
                        symbols.add(sym)
        return symbols


def closure(items, grammar):
    closure_set = set(items)
    added = True
    while added:
        added = False
        new_items = set()
        for item in closure_set:
            sym = item.next_symbol()
            if sym in grammar.nonterminals:
                for prod in grammar.productions[sym]:
                    new_items.add(Item(sym, prod, 0))
        if not new_items.issubset(closure_set):
            closure_set |= new_items
            added = True
    return closure_set


def goto(items, symbol, grammar):
    moved = {
        Item(i.head, i.body, i.dot + 1) for i in items if i.next_symbol() == symbol
    }
    return closure(moved, grammar) if moved else set()


def canonical_collection(grammar):
    start_item = Item(
        grammar.start_symbol, grammar.productions[grammar.start_symbol][0], 0
    )
    start_state = closure({start_item}, grammar)

    states = [start_state]
    transitions = {}
    added = True
    while added:
        added = False
        for state in list(states):
            for symbol in grammar.terminals | grammar.nonterminals:
                new_state = goto(state, symbol, grammar)
                if new_state:
                    if new_state not in states:
                        states.append(new_state)
                        added = True
                    transitions[(states.index(state), symbol)] = states.index(new_state)
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
                    for symbol in body:
                        first[head].update(first[symbol] - {"ε"})
                        if "ε" not in first[symbol]:
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
                        beta = body[i + 1 :]
                        first_beta = set()
                        if not beta:
                            first_beta.add("ε")
                        else:
                            nullable = True
                            for sym in beta:
                                first_beta |= first[sym] - {"ε"}
                                if "ε" not in first[sym]:
                                    nullable = False
                                    break
                            if nullable:
                                first_beta.add("ε")

                        before = len(follow[B])
                        follow[B] |= first_beta - {"ε"}
                        if "ε" in first_beta:
                            follow[B] |= follow[A]
                        if len(follow[B]) > before:
                            changed = True
    return follow


def build_parsing_table(grammar, states, transitions, first, follow):
    action = {}
    goto_table = {}
    conflicts = []

    for state_index, state in enumerate(states):
        # Handle shift actions first
        for sym in grammar.terminals:
            tgt = transitions.get((state_index, sym))
            if tgt is not None:
                action[(state_index, sym)] = ("shift", tgt)

        # Handle reduce actions
        for item in state:
            if item.is_complete():
                if item.head == grammar.start_symbol:
                    action[(state_index, "$")] = ("accept", None)
                else:
                    for a in follow[item.head]:
                        if (state_index, a) in action:
                            existing = action[(state_index, a)]
                            if existing[0] == "shift":
                                conflicts.append(
                                    f"State {state_index}, symbol '{a}': Shift-Reduce conflict resolved in favor of shift"
                                )
                                continue
                        action[(state_index, a)] = ("reduce", (item.head, item.body))

        # Handle goto actions
        for sym in grammar.nonterminals:
            tgt = transitions.get((state_index, sym))
            if tgt is not None:
                goto_table[(state_index, sym)] = tgt

    for conflict in conflicts:
        print(f"⚠️ {conflict}")

    return action, goto_table


class SLRParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first = compute_first(grammar)
        self.follow = compute_follow(grammar, self.first)
        self.states, self.transitions = canonical_collection(grammar)
        self.action_table, self.goto_table = build_parsing_table(
            grammar, self.states, self.transitions, self.first, self.follow
        )
        # self.reductions = []

    def parse(self, tokens):
        """Parse a list of token strings"""
        stack = [0]
        pointer = 0
        # self.reductions.clear()

        print(f"Starting parse with tokens: {tokens}")

        while True:
            state = stack[-1]
            lookahead = tokens[pointer] if pointer < len(tokens) else "$"
            action = self.action_table.get((state, lookahead))

            print(f"State: {state}, Lookahead: '{lookahead}', Action: {action}")

            if not action:
                print(f"Syntax error at token: {lookahead}")
                print(f"Available actions from state {state}:")
                for (s, sym), act in self.action_table.items():
                    if s == state:
                        print(f"  On '{sym}': {act}")
                return False

            kind = action[0]
            if kind == "shift":
                stack.append(action[1])
                pointer += 1
                print(f"  Shifted to state {action[1]}")
            elif kind == "reduce":
                head, body = action[1]
                print(f"  Reducing by {head} → {' '.join(body) if body else 'ε'}")
                for _ in body:
                    stack.pop()
                state = stack[-1]
                goto_state = self.goto_table.get((state, head))
                if goto_state is None:
                    print(f"Internal parser error: no goto from {state} on {head}")
                    return False
                stack.append(goto_state)
                # record each successful reduction
                # self.reductions.append((head, body))
                print(f"  Goto state {goto_state}")
            elif kind == "accept":
                print("Parsing successful!")
                return True

    def parse_tokens(self, token_objects):
        """Parse a list of Token objects by converting them to strings"""
        token_strings = []
        for token in token_objects:
            if token.type in [TokenType.IDENT, TokenType.NUMBER, TokenType.STRING]:
                token_strings.append(token.type.value)
            else:
                token_strings.append(token.value)
        return self.parse(token_strings)


# ========================
# SPL Grammar Definition
# ========================
def build_spl_grammar():
    productions = {
        "S'": [["SPL_PROG"]],
        # Program structure
        "SPL_PROG": [
            [
                "glob",
                "{",
                "VARIABLES",
                "}",
                "proc",
                "{",
                "PROCDEFS",
                "}",
                "func",
                "{",
                "FUNCDEFS",
                "}",
                "main",
                "{",
                "MAINPROG",
                "}",
            ]
        ],
        # Variables
        "VARIABLES": [[], ["IDENT", "VARIABLES"]],
        # Procedures
        "PROCDEFS": [[], ["PDEF", "PROCDEFS"]],
        "PDEF": [["IDENT", "(", "PARAM", ")", "{", "BODY", "}"]],
        # Functions
        "FUNCDEFS": [[], ["FDEF", "FUNCDEFS"]],
        "FDEF": [["IDENT", "(", "PARAM", ")", "{", "BODY", ";", "return", "ATOM", "}"]],
        # Parameters & locals
        "PARAM": [["MAXTHREE"]],
        "MAXTHREE": [[], ["IDENT"], ["IDENT", "IDENT"], ["IDENT", "IDENT", "IDENT"]],
        "BODY": [["local", "{", "MAXTHREE", "}", "ALGO"]],
        # Main program
        "MAINPROG": [["var", "{", "VARIABLES", "}", "ALGO"]],
        # Algorithm (sequence of instructions)
        "ALGO": [["INSTR"], ["INSTR", ";", "ALGO"]],
        # Instructions
        "INSTR": [
            ["halt"],
            ["print", "OUTPUT"],
            ["ASSIGN"],
            ["IDENT", "(", "INPUT", ")"],  # procedure call
            ["LOOP"],
            ["BRANCH"],
        ],
        # Assignments
        "ASSIGN": [["IDENT", "=", "IDENT", "(", "INPUT", ")"], ["IDENT", "=", "TERM"]],
        # Input arguments (max 3)
        "INPUT": [[], ["ATOM"], ["ATOM", "ATOM"], ["ATOM", "ATOM", "ATOM"]],
        # Output
        "OUTPUT": [["ATOM"], ["STRING"]],
        # Atoms
        "ATOM": [["IDENT"], ["NUMBER"]],
        # Terms (expressions)
        "TERM": [
            ["ATOM"],
            ["(", "UNOP", "TERM", ")"],
            ["(", "TERM", "BINOP", "TERM", ")"],
        ],
        "UNOP": [["neg"], ["not"]],
        "BINOP": [
            ["eq"],
            [">"],
            ["or"],
            ["and"],
            ["plus"],
            ["minus"],
            ["mult"],
            ["div"],
        ],
        # Loops
        "LOOP": [
            ["while", "TERM", "{", "ALGO", "}"],
            ["do", "{", "ALGO", "}", "until", "TERM"],
        ],
        # Branches
        "BRANCH": [
            ["if", "TERM", "{", "ALGO", "}"],
            ["if", "TERM", "{", "ALGO", "}", "else", "{", "ALGO", "}"],
        ],
    }

    return Grammar("S'", productions)


# ========================
# Test Functions
# ========================
def test_simple_program():
    """Test with a simple SPL program"""
    grammar = build_spl_grammar()
    parser = SLRParser(grammar)

    # Create token objects like your lexer would produce
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
        # Algorithm: localVar = 42; print localVar
        Token(TokenType.IDENT, "localVar"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.NUMBER, "42"),
        Token(TokenType.SEMI, ";"),
        Token(TokenType.PRINT, "print"),
        Token(TokenType.IDENT, "localVar"),
        Token(TokenType.RBRACE, "}"),
    ]

    print("Testing SPL program:")
    print("glob { globalVar }")
    print("proc { }")
    print("func { }")
    print("main { var { localVar } localVar = 42; print localVar }")
    print()

    return parser.parse_tokens(tokens)


def test_with_string_tokens():
    """Test with string tokens directly"""
    grammar = build_spl_grammar()
    parser = SLRParser(grammar)

    tokens = [
        "glob",
        "{",
        "IDENT",
        "}",
        "proc",
        "{",
        "}",
        "func",
        "{",
        "}",
        "main",
        "{",
        "var",
        "{",
        "IDENT",
        "}",
        "IDENT",
        "=",
        "NUMBER",
        ";",
        "print",
        "IDENT",
        "}",
    ]

    print("Testing with string tokens:", tokens)
    return parser.parse(tokens)


if __name__ == "__main__":
    print("=== Test 1: With Token Objects ===")
    result1 = test_simple_program()

    print("\n=== Test 2: With String Tokens ===")
    result2 = test_with_string_tokens()

    print(f"\nResults: Token objects: {result1}, String tokens: {result2}")
