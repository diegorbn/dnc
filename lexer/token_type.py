from enum import Enum, auto

class TokenType(Enum):
    INT = auto()
    BOOL = auto()
    MONDONGO = auto()
    IF = auto()
    ELSE = auto()

    IDENT = auto()
    INT_LITERAL = auto()

    PLUS = auto()
    ASSIGN = auto()
    SEMICOLON = auto()

    WHILE = auto()

    PRINT = auto()

    TRUE = auto()
    FALSE = auto()