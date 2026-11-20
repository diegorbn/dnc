"""Recursive-descent parser and abstract syntax tree for DNC."""

from .dnc_parser import Parser, ParserError

__all__ = ["Parser", "ParserError"]
