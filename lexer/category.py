"""Character categories and symbols defined by the DNC grammar."""

from string import ascii_letters, digits

from .token_type import TokenType

IDENT_START = ascii_letters + "_"
IDENT_CONTINUE = IDENT_START + digits
DIGITS = digits

KEYWORDS = {
    "int": TokenType.INT,
    "bool": TokenType.BOOL,
    "mondongo": TokenType.MONDONGO,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.ASSIGN,
    "==": TokenType.EQUAL,
    "!": TokenType.BANG,
    "!=": TokenType.NOT_EQUAL,
    "<": TokenType.LESS,
    "<=": TokenType.LESS_EQUAL,
    ">": TokenType.GREATER,
    ">=": TokenType.GREATER_EQUAL,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ";": TokenType.SEMICOLON,
}
