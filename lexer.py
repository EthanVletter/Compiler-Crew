from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import json

class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"Lexing error at line {line}, col {col}: {message}")
        self.line = line
        self.col = col

@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    col: int

class TokenType(str, Enum):
    # punctuation / symbols
    LPAREN = "LPAREN"       # (
    RPAREN = "RPAREN"       # )
    LBRACE = "LBRACE"       # {
    RBRACE = "RBRACE"       # }
    SEMI = "SEMI"           # ;
    ASSIGN = "ASSIGN"       # =
    GT = "GT"               # >

    # literals / identifiers
    IDENT = "IDENT"         # user-defined name
    NUMBER = "NUMBER"       # 0 | [1-9][0-9]*
    STRING = "STRING"       # "letters|digits", max length 15

    # keywords (as words in the language)
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

    # unary ops
    NEG = "neg"
    NOT = "not"

    # binary ops (word operators)
    EQ = "eq"
    OR = "or"
    AND = "and"
    PLUS = "plus"
    MINUS = "minus"
    MULT = "mult"
    DIV = "div"

    EOF = "EOF"

# keyword string -> TokenType (only the lowercase-valued items)
KEYWORDS = {t.value: t for t in TokenType if t.value.islower()}

class Lexer:
    """
    SPL lexer with the following rules:
      - Whitespace separates tokens (no token contains whitespace).
      - Identifiers: [a-z][a-z0-9]* and must not be a keyword.
      - Numbers: 0 or [1-9][0-9]* (no leading zeros like 01).
      - Strings: double-quoted; only letters/digits inside; length <= 15; cannot span lines.
      - Keywords listed in KEYWORDS are recognized (take precedence over IDENT).
      - Symbols: () {} ; = >
    """
    def __init__(self, source: str):
        self.source = source
        self.n = len(source)
        self.i = 0
        self.line = 1
        self.col = 1

    # --- helpers ---
    def _peek(self) -> str:
        return self.source[self.i] if self.i < self.n else ""

    def _advance(self) -> str:
        ch = self._peek()
        if not ch:
            return ""
        self.i += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _make(self, ttype: TokenType, value: str, line: int, col: int) -> Token:
        return Token(ttype.value, value, line, col)

    def _skip_whitespace(self):
        while self.i < self.n and self._peek() in " \t\r\n":
            self._advance()

    # --- scanners for specific token kinds ---
    def _read_string(self) -> Token:
        # precondition: current char is '"'
        start_line, start_col = self.line, self.col
        self._advance()  # consume opening "
        chars = []
        while True:
            ch = self._peek()
            if ch == "":
                raise LexerError("Unterminated string literal", start_line, start_col)
            if ch == '"':
                self._advance()  # consume closing "
                break
            if ch == "\n":
                raise LexerError("String literal cannot span lines", self.line, self.col)
            # only letters/digits allowed inside strings
            if not (ch.isalpha() or ch.isdigit()):
                raise LexerError("Strings may contain only letters or digits", self.line, self.col)
            chars.append(ch)
            self._advance()
        if len(chars) > 15:
            raise LexerError("String literal exceeds max length 15", start_line, start_col)
        return self._make(TokenType.STRING, "".join(chars), start_line, start_col)

    def _read_ident_or_keyword(self) -> Token:
        start_i = self.i
        start_line, start_col = self.line, self.col
        # first char: [a-z]
        self._advance()
        while self.i < self.n:
            ch = self._peek()
            if ch.islower() or ch.isdigit():
                self._advance()
            else:
                break
        lexeme = self.source[start_i:self.i]

        # keywords first
        if lexeme in KEYWORDS:
            return self._make(KEYWORDS[lexeme], lexeme, start_line, start_col)
        # otherwise IDENT
        return self._make(TokenType.IDENT, lexeme, start_line, start_col)

    def _read_number(self) -> Token:
        start_i = self.i
        start_line, start_col = self.line, self.col
        if self._peek() == "0":
            self._advance()
            # reject 0 followed by more digits
            if self.i < self.n and self._peek().isdigit():
                raise LexerError("Numbers cannot have leading zeros", start_line, start_col)
        else:
            if not self._peek().isdigit() or self._peek() == "0":
                raise LexerError("Invalid number start", start_line, start_col)
            while self.i < self.n and self._peek().isdigit():
                self._advance()
        return self._make(TokenType.NUMBER, self.source[start_i:self.i], start_line, start_col)

    # --- iteration ---
    def __iter__(self):
        return self

    def __next__(self) -> Token:
        self._skip_whitespace()
        if self.i >= self.n:
            raise StopIteration

        ch = self._peek()
        line, col = self.line, self.col

        # single-char punctuation
        if ch == "(":
            self._advance(); return self._make(TokenType.LPAREN, "(", line, col)
        if ch == ")":
            self._advance(); return self._make(TokenType.RPAREN, ")", line, col)
        if ch == "{":
            self._advance(); return self._make(TokenType.LBRACE, "{", line, col)
        if ch == "}":
            self._advance(); return self._make(TokenType.RBRACE, "}", line, col)
        if ch == ";":
            self._advance(); return self._make(TokenType.SEMI, ";", line, col)
        if ch == "=":
            self._advance(); return self._make(TokenType.ASSIGN, "=", line, col)
        if ch == ">":
            self._advance(); return self._make(TokenType.GT, ">", line, col)

        # strings
        if ch == '"':
            return self._read_string()

        # numbers
        if ch.isdigit():
            return self._read_number()

        # identifiers / keywords (must start lowercase)
        if "a" <= ch <= "z":
            return self._read_ident_or_keyword()

        # nothing matched
        raise LexerError(f"Unexpected character {repr(ch)}", line, col)


