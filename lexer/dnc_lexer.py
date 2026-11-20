"""Turn DNC source text into a sequence of tokens."""

from .category import DIGITS, IDENT_CONTINUE, IDENT_START, KEYWORDS, SYMBOLS
from .token import Token
from .token_type import TokenType


class Lexer:
    """Scan source text into tokens, tracking one-based line and column positions."""

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def _consume(self):
        """Consume one character and update the position of the next character."""
        char = self.source[self.position]
        self.position += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self):
        """Scan and return one token, or raise ValueError for an unknown character.

        Whitespace is skipped. At the end of the source, return an EOF token
        with an empty lexeme. This method does not add the token to the list.
        """
        while self.position < len(self.source) and self.source[self.position].isspace():
            self._consume()

        line, column = self.line, self.column
        if self.position == len(self.source):
            return Token(TokenType.EOF, "", line, column)

        start = self.position
        char = self.source[self.position]
        if char in IDENT_START:
            while self.position < len(self.source) and self.source[self.position] in IDENT_CONTINUE:
                self._consume()
            lexeme = self.source[start:self.position]
            return Token(KEYWORDS.get(lexeme, TokenType.IDENT), lexeme, line, column)
        if char in DIGITS:
            while self.position < len(self.source) and self.source[self.position] in DIGITS:
                self._consume()
            return Token(TokenType.INT_LITERAL, self.source[start:self.position], line, column)

        # Match two-character operators before their single-character prefixes.
        pair = self.source[self.position:self.position + 2]
        if len(pair) == 2 and pair in SYMBOLS:
            self._consume()
            self._consume()
            return Token(SYMBOLS[pair], pair, line, column)
        if char in SYMBOLS:
            self._consume()
            return Token(SYMBOLS[char], char, line, column)
        raise ValueError(f"Carácter inesperado {char!r} en la línea {line}, columna {column}")

    def advance(self):
        """Scan and return the next token without storing it."""
        return self.tokenize()

    def scan(self):
        """Store remaining tokens through EOF; repeated calls after EOF do nothing."""
        if self.tokens and self.tokens[-1].type == TokenType.EOF:
            return
        while True:
            token = self.advance()
            self.tokens.append(token)
            if token.type == TokenType.EOF:
                return

    def get_all_tokens(self):
        """Return the token list populated by scan()."""
        return self.tokens
