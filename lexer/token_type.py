from enum import Enum, auto

class TokenType(Enum):
    """Token categories recognized by the lexer."""

    INT = auto()  # int
    BOOL = auto()  # bool
    MONDONGO = auto()  # mondongo
    IF = auto()  # if
    ELSE = auto()  # else

    IDENT = auto()  # Identifier, e.g. count
    INT_LITERAL = auto()  # Integer literal, e.g. 42

    PLUS = auto()  # +
    ASSIGN = auto()  # =
    SEMICOLON = auto()  # ;

    WHILE = auto()  # while

    PRINT = auto()  # print

    TRUE = auto()  # true
    FALSE = auto()  # false
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    EQUAL = auto()  # ==
    NOT_EQUAL = auto()  # !=
    BANG = auto()  # !
    LESS = auto()  # <
    LESS_EQUAL = auto()  # <=
    GREATER = auto()  # >
    GREATER_EQUAL = auto()  # >=
    LEFT_PAREN = auto()  # (
    RIGHT_PAREN = auto()  # )
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto()  # }
    EOF = auto()  # End of source
