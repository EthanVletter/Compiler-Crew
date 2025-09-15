from collections import defaultdict

class SLRParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first = compute_first(grammar)
        self.follow = compute_follow(grammar, self.first)

        # Build states and tables
        self.states, self.transitions = canonical_collection(grammar)
        self.action_table, self.goto_table = build_parsing_table(
            grammar, self.states, self.transitions, self.first, self.follow
        )

    def parse(self, tokens):
        stack = [0]  # initial state
        pointer = 0

        while True:
            state = stack[-1]
            lookahead = tokens[pointer] if pointer < len(tokens) else "$"

            action = self.action_table.get((state, lookahead))

            if not action:
                print(f"Syntax error at token: {lookahead}")
                return False

            if action[0] == "shift":
                stack.append(action[1])
                pointer += 1

            elif action[0] == "reduce":
                head, body = action[1]
                for sym in body:
                    if sym != "ε":  # pop for non-epsilon symbols
                        stack.pop()
                state = stack[-1]
                stack.append(self.goto_table[(state, head)])

            elif action[0] == "accept":
                print("Parsing successful!")
                return True

# ========================
# Grammar Representation
# ========================
class Grammar:
    def __init__(self, start_symbol, productions):
        # normalize: convert ["ε"] to [] everywhere
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

# ========================
# LR(0) Item
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
        return (self.head, tuple(self.body), self.dot) == (other.head, tuple(other.body), other.dot)

    def __hash__(self):
        return hash((self.head, tuple(self.body), self.dot))

    def __repr__(self):
        body = self.body[:]
        body.insert(self.dot, "•")
        return f"{self.head} → {' '.join(body)}"


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
    moved = {Item(i.head, i.body, i.dot + 1)
             for i in items if i.next_symbol() == symbol}
    return closure(moved, grammar) if moved else set()


# ========================
# Canonical Collection of LR(0) Items
# ========================
def canonical_collection(grammar):
    start_item = Item(grammar.start_symbol, grammar.productions[grammar.start_symbol][0], 0)
    start_state = closure({start_item}, grammar)

    states = [start_state]
    transitions = {}
    added = True
    while added:
        added = False
        for state in list(states):
            for symbol in grammar.terminals | grammar.nonterminals:
                new_state = goto(state, symbol, grammar)
                if new_state and new_state not in states:
                    states.append(new_state)
                    added = True
                if new_state:
                    transitions[(states.index(state), symbol)] = states.index(new_state) if new_state in states else len(states)
    return states, transitions


# ========================
# FIRST and FOLLOW
# ========================
def compute_first(grammar):
    first = defaultdict(set)

    # Terminals: FIRST(t) = {t}
    for t in grammar.terminals:
        first[t].add(t)

    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.productions.items():
            for body in bodies:
                before = len(first[head])
                if not body:  # ε-production
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
    follow[grammar.start_symbol].add("$")  # end marker

    changed = True
    while changed:
        changed = False
        for head, bodies in grammar.productions.items():
            for body in bodies:
                trailer = follow[head].copy()
                for symbol in reversed(body):
                    if symbol in grammar.nonterminals:
                        before = len(follow[symbol])
                        follow[symbol].update(trailer)
                        # If ε in FIRST(symbol), trailer expands
                        if "ε" in first[symbol]:
                            trailer = trailer.union(first[symbol] - {"ε"})
                        else:
                            trailer = first[symbol]
                        if len(follow[symbol]) > before:
                            changed = True
                    else:
                        trailer = {symbol}  # terminal resets trailer
    return follow


def build_parsing_table(grammar, states, transitions, first, follow):
    action = {}
    goto_table = {}

    for state_index, state in enumerate(states):
        for item in state:
            # Case 1: Shift
            sym = item.next_symbol()
            if sym and sym in grammar.terminals:
                if (state_index, sym) in transitions:
                    action[(state_index, sym)] = ("shift", transitions[(state_index, sym)])

            # Case 2: Reduce
            if item.is_complete() and item.head != grammar.start_symbol:
                for a in follow[item.head]:
                    action[(state_index, a)] = ("reduce", (item.head, item.body))

            # Case 3: Accept
            if item.is_complete() and item.head == grammar.start_symbol:
                action[(state_index, "$")] = ("accept", None)

        # GOTO table
        for sym in grammar.nonterminals:
            if (state_index, sym) in transitions:
                goto_table[(state_index, sym)] = transitions[(state_index, sym)]

    return action, goto_table


# ========================
# SPL Grammar (subset for testing)
# ========================
def build_spl_grammar():
    productions = {
        "S'": [["SPL_PROG"]],
        "SPL_PROG": [["glob", "{", "VARIABLES", "}", 
                      "proc", "{", "PROCDEFS", "}", 
                      "func", "{", "FUNCDEFS", "}", 
                      "main", "{", "MAINPROG", "}"]],

        # VARIABLES
        "VARIABLES": [[], ["VAR", "VARIABLES"]],
        "VAR": [["NAME"]],
        "NAME": [["id"]],   # "id" = user-defined name

        # PROCDEFS
        "PROCDEFS": [[], ["PDEF", "PROCDEFS"]],
        "PDEF": [["NAME","(","PARAM",")","{","BODY","}"]],

        # FUNCDEFS
        "FUNCDEFS": [[], ["FDEF","FUNCDEFS"]],
        "FDEF": [["NAME","(","PARAM",")","{","FUNC_BODY","}"]],
        # Function body must be ALGO followed by "; return ATOM"
        "FUNC_BODY": [["ALGO",";","return","ATOM"]],

        # MAIN
        "MAINPROG": [["var","{","VARIABLES","}","ALGO"]],

        # BODY (inside procedures)
        "BODY": [[], ["ALGO"]],

        # ALGO & INSTR
        "ALGO": [["INSTR"], ["INSTR",";","ALGO"]],
        "INSTR": [
            ["halt"],
            ["print","OUTPUT"],
            ["ASSIGN"],
            ["NAME","(","INPUT",")"],
            ["LOOP"],
            ["BRANCH"]
        ],

        # ASSIGN
        "ASSIGN": [
            ["VAR","=","NAME","(","INPUT",")"],
            ["VAR","=","TERM"]
        ],

        # INPUT (max 3 arguments)
        "INPUT": [[], ["ATOM"], ["ATOM","ATOM"], ["ATOM","ATOM","ATOM"]],

        # OUTPUT
        "OUTPUT": [["ATOM"], ["string"]],

        # ATOM
        "ATOM": [["VAR"], ["number"]],

        # TERM / expressions
        "TERM": [["ATOM"], ["(","UNOP","TERM",")"], ["(","TERM","BINOP","TERM",")"]],
        "UNOP": [["neg"], ["not"]],
        "BINOP": [["eq"], [">"], ["or"], ["and"], ["plus"], ["minus"], ["mult"], ["div"]],

        # LOOPS
        "LOOP": [["while","TERM","{","ALGO","}"], ["do","{","ALGO","}","until","TERM"]],

        # BRANCHES
        "BRANCH": [["if","TERM","{","ALGO","}"], ["if","TERM","{","ALGO","}","else","{","ALGO","}"]],

        # PARAMS (max 3)
        "PARAM": [[], ["NAME"], ["NAME","NAME"], ["NAME","NAME","NAME"]],
    }

    return Grammar("S'", productions)

def test_states():
    grammar = build_spl_grammar()
    states, transitions = canonical_collection(grammar)

    print("=== Canonical States ===")
    for i, st in enumerate(states):
        print(f"State {i}:")
        for it in st:
            print(" ", it)

    print("\n=== Transitions ===")
    for (s, sym), t in transitions.items():
        print(f"From state {s} on {sym} → state {t}")

def test_parser():
    grammar = build_spl_grammar()
    parser = SLRParser(grammar)

    # Example SPL program tokens (minimal)
    tokens = ["glob","{","}","proc","{","}","func","{","}","main","{","var","{","id","}","id","=","number",";","print","number",";","halt","}","$"]

    parser.parse(tokens)
    
# ========================
# Driver
# ========================
def main():
    grammar = build_spl_grammar()
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)

    print("=== FIRST sets ===")
    for nt in grammar.nonterminals:
        print(f"{nt}: {first[nt]}")

    print("\n=== FOLLOW sets ===")
    for nt in grammar.nonterminals:
        print(f"{nt}: {follow[nt]}")

if __name__ == "__main__":
    # main()
    # test_states()
    # test_negative_cases()
    test_parser()