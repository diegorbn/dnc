"""Simple syntax tree nodes; tokens preserve their source locations."""

from dataclasses import dataclass
from typing import Optional

from lexer.token import Token


@dataclass
class Program:
    body: 'Block'


@dataclass
class Block:
    statements: list


@dataclass
class Declaration:
    type_token: Token
    name_token: Token
    initializer: Optional[object]


@dataclass
class Assignment:
    name_token: Token
    value: object


@dataclass
class Print:
    value: object


@dataclass
class If:
    condition: object
    then_block: Block
    else_block: Optional[Block]


@dataclass
class While:
    condition: object
    body: Block


@dataclass
class IntLiteral:
    token: Token


@dataclass
class BoolLiteral:
    token: Token


@dataclass
class Identifier:
    token: Token


@dataclass
class Unary:
    operator_token: Token
    operand: object


@dataclass
class Binary:
    operator_token: Token
    left: object
    right: object
