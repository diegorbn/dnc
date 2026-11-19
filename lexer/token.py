from dataclasses import dataclass
from token_type import TokenType

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int