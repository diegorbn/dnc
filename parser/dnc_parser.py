"""Predictive recursive-descent parser for the DNC grammar."""

from lexer.token_type import TokenType as T
from . import ast


class ParserError(Exception):
    """A syntax error at a particular token."""

    def __init__(self, message, token):
        """Attach the offending token and its location to the error message."""
        self.token = token
        super().__init__(
            f"{message}; se encontró {token.type.name} {token.lexeme!r} "
            f"en la línea {token.line}, columna {token.column}"
        )


class Parser:
    """Parse a lexer token list into a DNC abstract syntax tree."""

    def __init__(self, tokens):
        """Initialize the parser with tokens ending in exactly one EOF token."""
        if not tokens or tokens[-1].type != T.EOF or any(
            token.type == T.EOF for token in tokens[:-1]
        ):
            raise ValueError("La lista de tokens debe terminar con un único token EOF")
        self.tokens = tokens
        self.position = 0

    def peek(self):
        """Return the current token without consuming it."""
        return self.tokens[self.position]

    def advance(self):
        """Return and consume the current token, leaving EOF in place."""
        token = self.peek()
        if token.type != T.EOF:
            self.position += 1
        return token

    def check(self, token_type):
        """Return whether the current token has the requested type."""
        return self.peek().type == token_type

    def expect(self, token_type):
        """Consume the expected token or raise a location-aware syntax error."""
        if not self.check(token_type):
            raise ParserError(f"Se esperaba {token_type.name}", self.peek())
        return self.advance()

    def parse_program(self):
        """Parse the entry point and require the end of the token list."""
        body = self.parse_main_function()
        self.expect(T.EOF)
        return ast.Program(body)

    def parse_main_function(self):
        """Parse the mandatory mondongo entry point and return its block."""
        self.expect(T.INT)
        self.expect(T.MONDONGO)
        self.expect(T.LEFT_PAREN)
        self.expect(T.RIGHT_PAREN)
        return self.parse_block()

    def parse_block(self):
        """Parse a brace-delimited sequence of statements."""
        self.expect(T.LEFT_BRACE)
        statements = []
        while not self.check(T.RIGHT_BRACE):
            if self.check(T.EOF):
                raise ParserError("Se esperaba RIGHT_BRACE", self.peek())
            statements.append(self.parse_statement())
        self.expect(T.RIGHT_BRACE)
        return ast.Block(statements)

    def parse_statement(self):
        """Parse the statement indicated by the current token."""
        token_type = self.peek().type
        if token_type in (T.INT, T.BOOL):
            return self.parse_declaration()
        if token_type == T.IDENT:
            return self.parse_assignment()
        if token_type == T.PRINT:
            return self.parse_print()
        if token_type == T.IF:
            return self.parse_if()
        if token_type == T.WHILE:
            return self.parse_while()
        if token_type == T.LEFT_BRACE:
            return self.parse_block()
        raise ParserError("Se esperaba una sentencia", self.peek())

    def parse_type(self):
        """Consume and return an int or bool type token."""
        if self.peek().type not in (T.INT, T.BOOL):
            raise ParserError("Se esperaba INT o BOOL", self.peek())
        return self.advance()

    def parse_declaration(self):
        """Parse a variable declaration with an optional initializer."""
        type_token = self.parse_type()
        name = self.expect(T.IDENT)
        initializer = None
        if self.check(T.ASSIGN):
            self.advance()
            initializer = self.parse_expression()
        self.expect(T.SEMICOLON)
        return ast.Declaration(type_token, name, initializer)

    def parse_assignment(self):
        """Parse an assignment to an identifier."""
        name = self.expect(T.IDENT)
        self.expect(T.ASSIGN)
        value = self.parse_expression()
        self.expect(T.SEMICOLON)
        return ast.Assignment(name, value)

    def parse_print(self):
        """Parse a print statement and its expression."""
        self.expect(T.PRINT)
        self.expect(T.LEFT_PAREN)
        value = self.parse_expression()
        self.expect(T.RIGHT_PAREN)
        self.expect(T.SEMICOLON)
        return ast.Print(value)

    def parse_if(self):
        """Parse an if statement and its optional else block."""
        self.expect(T.IF)
        self.expect(T.LEFT_PAREN)
        condition = self.parse_expression()
        self.expect(T.RIGHT_PAREN)
        then_block = self.parse_block()
        else_block = None
        if self.check(T.ELSE):
            self.advance()
            else_block = self.parse_block()
        return ast.If(condition, then_block, else_block)

    def parse_while(self):
        """Parse a while statement and its body."""
        self.expect(T.WHILE)
        self.expect(T.LEFT_PAREN)
        condition = self.parse_expression()
        self.expect(T.RIGHT_PAREN)
        return ast.While(condition, self.parse_block())

    def parse_expression(self):
        """Parse an additive expression with at most one comparison."""
        left = self.parse_additive()
        if self.peek().type in (T.EQUAL, T.NOT_EQUAL, T.LESS, T.LESS_EQUAL,
                                T.GREATER, T.GREATER_EQUAL):
            op = self.advance()
            left = ast.Binary(op, left, self.parse_additive())
        return left

    def parse_additive(self):
        """Parse left-associative addition and subtraction."""
        left = self.parse_multiplicative()
        while self.peek().type in (T.PLUS, T.MINUS):
            op = self.advance()
            left = ast.Binary(op, left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        """Parse left-associative multiplication and division."""
        left = self.parse_unary()
        while self.peek().type in (T.STAR, T.SLASH):
            op = self.advance()
            left = ast.Binary(op, left, self.parse_unary())
        return left

    def parse_unary(self):
        """Parse a unary operator and operand, or a primary expression."""
        if self.peek().type in (T.PLUS, T.MINUS, T.BANG):
            op = self.advance()
            return ast.Unary(op, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        """Parse a literal, identifier, or parenthesized expression."""
        token_type = self.peek().type
        if token_type == T.INT_LITERAL:
            return ast.IntLiteral(self.advance())
        if token_type in (T.TRUE, T.FALSE):
            return ast.BoolLiteral(self.advance())
        if token_type == T.IDENT:
            return ast.Identifier(self.advance())
        if token_type == T.LEFT_PAREN:
            self.advance()
            expression = self.parse_expression()
            self.expect(T.RIGHT_PAREN)
            return expression
        raise ParserError("Se esperaba una expresión", self.peek())
