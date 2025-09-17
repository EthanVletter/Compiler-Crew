#Run with pytest -q

from dataclasses import asdict

from lexer import Lexer, LexerError, TokenType

# Helper: tokenize and return (type, value) pairs for easy assertions
def toks(src):
    return [(t.type, t.value) for t in Lexer(src)]

def print_tokens(src):
    out = []
    for t in Lexer(src):
        out.append(f"{t.type}:{t.value}@{t.line}:{t.col}")
    return "\n".join(out)


#Simple sample test
SAMPLE = """\
glob { x y }
proc { }
func { }
main {
  var { a b1 }
  print "Hello123"
  a = 0;
  while (neg 1) { halt }
  if (eq 1 1) { print "ok" } else { halt }
}
"""

def test_sample_program_tokens():
    got = toks(SAMPLE)
    assert got[:6] == [
        (TokenType.GLOB.value, "glob"),
        (TokenType.LBRACE.value, "{"),
        (TokenType.IDENT.value, "x"),
        (TokenType.IDENT.value, "y"),
        (TokenType.RBRACE.value, "}"),
        (TokenType.PROC.value, "proc"),
    ]
    assert (TokenType.VAR.value, "var") in got
    assert (TokenType.PRINT.value, "print") in got
    assert (TokenType.STRING.value, "Hello123") in got
    assert (TokenType.WHILE.value, "while") in got
    assert (TokenType.NEG.value, "neg") in got
    assert (TokenType.HALT.value, "halt") in got
    assert (TokenType.IF.value, "if") in got
    assert (TokenType.EQ.value, "eq") in got
    assert (TokenType.ELSE.value, "else") in got

# Expected (prefix of) output (types:values):
# GLOB:glob  LBRACE:{  IDENT:x  IDENT:y  RBRACE:}
# PROC:proc  LBRACE:{  RBRACE:}
# FUNC:func  LBRACE:{  RBRACE:}
# MAIN:main  LBRACE:{
# VAR:var  LBRACE:{  IDENT:a  IDENT:b1  RBRACE:}
# PRINT:print  STRING:Hello123
# IDENT:a  ASSIGN:=  NUMBER:0  SEMI:;
# WHILE:while  LPAREN:(  NEG:neg  NUMBER:1  RPAREN:)  LBRACE:{  HALT:halt  RBRACE:}
# IF:if  LPAREN:(  EQ:eq  NUMBER:1  NUMBER:1  RPAREN:)
# LBRACE:{  PRINT:print  STRING:ok  RBRACE:}  ELSE:else  LBRACE:{  HALT:halt  RBRACE:}
# RBRACE:}


#Distinguishing keywords from identifiers
def test_keywords_vs_identifiers():
    src = "print printx plus plus9 and andy not noteq"
    got = toks(src)
    assert got == [
        (TokenType.PRINT.value, "print"),
        (TokenType.IDENT.value, "printx"),
        (TokenType.PLUS.value, "plus"),
        (TokenType.IDENT.value, "plus9"),
        (TokenType.AND.value, "and"),
        (TokenType.IDENT.value, "andy"),
        (TokenType.NOT.value, "not"),
        (TokenType.IDENT.value, "noteq"),
    ]

# Expected:
# PRINT:print, IDENT:printx, PLUS:plus, IDENT:plus9,
# AND:and, IDENT:andy, NOT:not, IDENT:noteq


#Identifier rules
def test_identifier_minimal_and_digits():
    assert toks("a z9 a1") == [
        (TokenType.IDENT.value, "a"),
        (TokenType.IDENT.value, "z9"),
        (TokenType.IDENT.value, "a1"),
    ]

def test_identifier_reject_uppercase_start():
    try:
        _ = toks("A")
        assert False, "Expected LexerError for uppercase start"
    except LexerError as e:
        assert "Unexpected character" in str(e) or "must start" in str(e)

def test_identifier_reject_underscore():
    try:
        _ = toks("a_")
        assert False, "Expected LexerError for underscore"
    except LexerError as e:
        assert "Unexpected character" in str(e) or "Strings may contain" not in str(e)

# Expected:
# "a z9 a1" -> IDENT:a, IDENT:z9, IDENT:a1
# "A" -> LexerError (uppercase not allowed at start)
# "a_" -> LexerError (underscore not allowed anywhere)


#Numbers
def test_numbers_ok():
    assert toks("0 7 12345") == [
        (TokenType.NUMBER.value, "0"),
        (TokenType.NUMBER.value, "7"),
        (TokenType.NUMBER.value, "12345"),
    ]

def test_numbers_reject_leading_zero():
    try:
        _ = toks("01")
        assert False, "Expected LexerError for leading zero"
    except LexerError as e:
        assert "leading zeros" in str(e)

# Expected:
# "0 7 12345" -> NUMBER:0, NUMBER:7, NUMBER:12345
# "01" -> LexerError: Numbers cannot have leading zeros


#Strings
def test_string_ok_and_limits():
    # exactly 15 chars inside quotes is allowed
    s15 = '"abcdefghijklmno"'  # 15
    assert toks(s15) == [(TokenType.STRING.value, "abcdefghijklmno")]

def test_string_too_long():
    s16 = '"abcdefghijklmnop"'  # 16
    try:
        _ = toks(s16)
        assert False, "Expected LexerError for string length > 15"
    except LexerError as e:
        assert "exceeds max length" in str(e)

def test_string_illegal_char():
    try:
        _ = toks('"abc_def"')
        assert False, "Expected LexerError for underscore in string"
    except LexerError as e:
        assert "only letters or digits" in str(e)

def test_string_unterminated():
    try:
        _ = toks('"abc')
        assert False, "Expected LexerError for unterminated string"
    except LexerError as e:
        assert "Unterminated string" in str(e)

def test_string_newline_forbidden():
    try:
        _ = toks('"ab\nc"')
        assert False, "Expected LexerError for newline in string"
    except LexerError as e:
        assert "cannot span lines" in str(e)

# Expected:
# '"abcdefghijklmno"' -> STRING:abcdefghijklmno
# '"abcdefghijklmnop"' -> LexerError: String literal exceeds max length 15
# '"abc_def"' -> LexerError: Strings may contain only letters or digits
# '"abc' -> LexerError: Unterminated string literal
# '"ab\nc"' -> LexerError: String literal cannot span lines


#Operators
def test_ops_word_and_symbol_gt():
    src = "eq and or plus minus mult div neg not >"
    got = toks(src)
    assert got == [
        (TokenType.EQ.value, "eq"),
        # (TokenType.GT.value, "gt"),
        (TokenType.AND.value, "and"),
        (TokenType.OR.value, "or"),
        (TokenType.PLUS.value, "plus"),
        (TokenType.MINUS.value, "minus"),
        (TokenType.MULT.value, "mult"),
        (TokenType.DIV.value, "div"),
        (TokenType.NEG.value, "neg"),
        (TokenType.NOT.value, "not"),
        (TokenType.GT.value, ">"), 
    ]

# Expected:
# EQ:eq, GT:gt, AND:and, OR:or, PLUS:plus, MINUS:minus,
# MULT:mult, DIV:div, NEG:neg, NOT:not, GT:>


#Punctuation, lines and columns
def test_punct_positions_basic():
    src = "(\n)\n{\n}\n;\n=\n" 
    lines = []
    for t in Lexer(src):
        lines.append((t.type, t.value, t.line, t.col))
    assert [x[0] for x in lines] == [
        TokenType.LPAREN.value, TokenType.RPAREN.value,
        TokenType.LBRACE.value, TokenType.RBRACE.value,
        TokenType.SEMI.value, TokenType.ASSIGN.value,
    ]

# Expected (types by line):
# 1: LPAREN:(   2: RPAREN:)   3: LBRACE:{   4: RBRACE:}
# 5: SEMI:;     6: ASSIGN:=   


#Unexpected characters
def test_unexpected_symbols():
    for bad in ["@", "#", "_", "$"]:
        try:
            _ = toks(bad)
            assert False, f"Expected LexerError for {bad}"
        except LexerError as e:
            assert "Unexpected character" in str(e)

# Expected:
# "@", "#", "_", "$" -> LexerError: Unexpected character ...


#Minimal constructs
def test_minimal_main_only():
    src = "glob { } proc { } func { } main { var { } halt }"
    got = toks(src)
    # make sure the core section headers and a `halt` are seen
    kinds = [k for k, _ in got]
    assert TokenType.GLOB.value in kinds
    assert TokenType.PROC.value in kinds
    assert TokenType.FUNC.value in kinds
    assert TokenType.MAIN.value in kinds
    assert (TokenType.HALT.value, "halt") in got

# Expected (subset):
# GLOB:glob { } PROC:proc { } FUNC:func { } MAIN:main { VAR:var { } HALT:halt }

#EDGE CASES AND ADDITIONAL TESTS

#Whitespace, empty
def test_empty_input():
    assert toks("") == []  # no tokens yielded 

def test_whitespace_only():
    assert toks(" \t \n  \r\n ") == []

#No space
def test_adjacent_braces_and_parens():
    src = "(){},{}();"
    try:
        toks(src)
        assert False, "Expected LexerError for ',' because its not in the lexer"
    except LexerError as e:
        assert "Unexpected character" in str(e)

def test_adjacent_without_comma():
    src = "(){}{}();"
    got = toks(src)
    # Expected sequence: '(', ')', '{', '}', '{', '}', '(', ')', ';'
    assert [t[0] for t in got] == [
        TokenType.LPAREN.value, TokenType.RPAREN.value,
        TokenType.LBRACE.value, TokenType.RBRACE.value,
        TokenType.LBRACE.value, TokenType.RBRACE.value,
        TokenType.LPAREN.value, TokenType.RPAREN.value,
        TokenType.SEMI.value
    ]

#Identifier boundaries
    assert toks("a a1 z99") == [
        (TokenType.IDENT.value, "a"),
        (TokenType.IDENT.value, "a1"),
        (TokenType.IDENT.value, "z99"),
    ]

def test_ident_uppercase_inside():
    # 'aA' should fail at 'A'
    try:
        toks("aA")
        assert False, "Expected LexerError for uppercase inside identifier"
    except LexerError as e:
        assert "Unexpected character" in str(e)

    # ensure keywords are exact match, not just prefixes
    assert toks("print printx and andy not noteq") == [
        (TokenType.PRINT.value, "print"),
        (TokenType.IDENT.value, "printx"),
        (TokenType.AND.value, "and"),
        (TokenType.IDENT.value, "andy"),
        (TokenType.NOT.value, "not"),
        (TokenType.IDENT.value, "noteq"),
    ]

#Number boundaries
    big = "12345678901234567890"
    assert toks(f"0 {big} 9") == [
        (TokenType.NUMBER.value, "0"),
        (TokenType.NUMBER.value, big),
        (TokenType.NUMBER.value, "9"),
    ]

def test_number_leading_zero_rejected():
    for s in ["01", "00", "0123"]:
        try:
            toks(s)
            assert False, f"Expected LexerError for leading zero: {s}"
        except LexerError as e:
            assert "leading zeros" in str(e)

#String boundaries
    assert toks('""') == [(TokenType.STRING.value, "")]
    assert toks('"abcdefghijklmno"') == [(TokenType.STRING.value, "abcdefghijklmno")]  # 15

def test_string_too_long_and_illegal_char():
    for s, msg in [('"abcdefghijklmnop"', "exceeds max length"), 
                   ('"hello!"', "only letters or digits")]:
        try:
            toks(s)
            assert False, f"Expected LexerError: {s}"
        except LexerError as e:
            assert msg in str(e)

def test_string_unterminated_and_newline():
    for s, msg in [('"abc', "Unterminated string"), ('"ab\nc"', "cannot span lines")]:
        try:
            toks(s)
            assert False, f"Expected LexerError: {s}"
        except LexerError as e:
            assert msg in str(e)

#Operators
    got = toks("eq and or plus minus mult div neg not >")
    assert got == [
        (TokenType.EQ.value, "eq"),
        # (TokenType.GT.value, "gt"),
        (TokenType.AND.value, "and"),
        (TokenType.OR.value, "or"),
        (TokenType.PLUS.value, "plus"),
        (TokenType.MINUS.value, "minus"),
        (TokenType.MULT.value, "mult"),
        (TokenType.DIV.value, "div"),
        (TokenType.NEG.value, "neg"),
        (TokenType.NOT.value, "not"),
        (TokenType.GT.value, ">"),
    ]

#Unexpected symbols
def test_unexpected_symbols_various():
    for bad in ["@", "#", "_", "$", "'", "`", "\\"]:
        try:
            toks(bad)
            assert False, f"Expected LexerError for {repr(bad)}"
        except LexerError as e:
            assert "Unexpected character" in str(e)

#Printing just to double check
if __name__ == "__main__":
    print("=== SAMPLE PROGRAM TOKENS (type:value@line:col) ===")
    print(print_tokens(SAMPLE))

    print("\n=== KEYWORDS VS IDENTIFIERS ===")
    print(print_tokens("print printx plus plus9 and andy not noteq"))

    print("\n=== IDENTIFIERS ===")
    print(print_tokens("a z9 a1"))

    print("\n=== NUMBERS ===")
    print(print_tokens("0 7 12345"))

    print("\n=== STRINGS ===")
    print(print_tokens('"abcdefghijklmno"'))

    print("\n=== OPERATORS (word + symbol) ===")
    print(print_tokens("eq gt and or plus minus mult div neg not >"))

    print("\n=== PUNCTUATION ===")
    print(print_tokens("( ) { } ; = >"))
