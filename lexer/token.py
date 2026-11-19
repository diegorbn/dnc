from dataclasses import dataclass
from .token_type import TokenType

@dataclass(frozen=True)
class Token:
    """A token's type, original text, and one-based starting location."""

    type: TokenType
    lexeme: str
    line: int
    column: int
