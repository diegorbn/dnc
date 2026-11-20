"""Check declarations, scopes and expression types without executing a program."""

from dataclasses import dataclass

from lexer.token import Token
from lexer.token_type import TokenType as T
from parser import ast


@dataclass(frozen=True)
class SemanticError:
    """A semantic diagnostic and the token where it occurred."""
    message: str
    token: Token

    def __str__(self):
        """Format the diagnostic with its source line and column."""
        return f"{self.message} en la línea {self.token.line}, columna {self.token.column}"


class SemanticAnalyzer:
    """Validate declarations, scopes, and types in a DNC syntax tree."""

    def __init__(self, on_scope_exit=None):
        """Initialize analysis state and an optional scope snapshot callback."""
        self.scopes: list[dict[str, T]] = []
        self.errors: list[SemanticError] = []
        self.on_scope_exit = on_scope_exit

    def enter_scope(self):
        """Push an empty scope onto the active scope stack."""
        self.scopes.append({})

    def exit_scope(self):
        """Report a copy of the current scope if requested, then remove it."""
        if self.on_scope_exit is not None:
            self.on_scope_exit(len(self.scopes) - 1, self.scopes[-1].copy())
        self.scopes.pop()

    def declare(self, token, variable_type):
        """Declare a variable in the current scope unless it already exists."""
        if token.lexeme in self.scopes[-1]:
            self.error(f"La variable '{token.lexeme}' ya está declarada en este ámbito", token)
            return False
        self.scopes[-1][token.lexeme] = variable_type
        return True

    def resolve(self, token):
        """Find an identifier's type in the nearest scope or record an error."""
        for scope in reversed(self.scopes):
            if token.lexeme in scope:
                return scope[token.lexeme]
        self.error(f"La variable '{token.lexeme}' no está declarada", token)
        return None

    def error(self, message, token):
        """Record a semantic diagnostic at the given token."""
        self.errors.append(SemanticError(message, token))

    def analyze(self, program):
        """Return True on success; diagnostics are available in errors."""
        self.errors.clear()
        self.scopes.clear()
        self.analyze_block(program.body)
        return not self.errors

    def analyze_block(self, block):
        """Analyze each statement in a new scope and remove it afterwards."""
        self.enter_scope()
        try:
            for statement in block.statements:
                self.analyze_statement(statement)
        finally:
            self.exit_scope()

    def analyze_statement(self, statement):
        """Check a statement's declarations, types, and nested blocks."""
        if isinstance(statement, ast.Block):
            self.analyze_block(statement)
        elif isinstance(statement, ast.Declaration):
            duplicate = statement.name_token.lexeme in self.scopes[-1]
            if duplicate:
                self.error(f"La variable '{statement.name_token.lexeme}' ya está declarada en este ámbito", statement.name_token)
            value_type = (self.analyze_expression(statement.initializer)
                          if statement.initializer is not None else None)
            if value_type is not None and value_type != statement.type_token.type:
                self.error(f"Tipos incompatibles en la inicialización de '{statement.name_token.lexeme}'", statement.name_token)
            if not duplicate:
                self.declare(statement.name_token, statement.type_token.type)
        elif isinstance(statement, ast.Assignment):
            target_type = self.resolve(statement.name_token)
            value_type = self.analyze_expression(statement.value)
            if target_type is not None and value_type is not None and target_type != value_type:
                self.error(f"Tipos incompatibles en la asignación a '{statement.name_token.lexeme}'", statement.name_token)
        elif isinstance(statement, ast.Print):
            self.analyze_expression(statement.value)
        elif isinstance(statement, (ast.If, ast.While)):
            condition_type = self.analyze_expression(statement.condition)
            if condition_type is not None and condition_type != T.BOOL:
                self.error("La condición debe ser de tipo bool", self.expression_token(statement.condition))
            if isinstance(statement, ast.If):
                self.analyze_block(statement.then_block)
                if statement.else_block is not None:
                    self.analyze_block(statement.else_block)
            else:
                self.analyze_block(statement.body)
        else:
            raise TypeError(f"Sentencia AST desconocida: {type(statement).__name__}")

    def expression_token(self, expression):
        """Return the expression's token for use in a diagnostic."""
        if isinstance(expression, (ast.Unary, ast.Binary)):
            return expression.operator_token
        return expression.token

    def analyze_expression(self, expression):
        """Check an expression and return its type, or None after an error."""
        if isinstance(expression, ast.IntLiteral):
            return T.INT
        if isinstance(expression, ast.BoolLiteral):
            return T.BOOL
        if isinstance(expression, ast.Identifier):
            return self.resolve(expression.token)
        if isinstance(expression, ast.Unary):
            operand_type = self.analyze_expression(expression.operand)
            expected = T.BOOL if expression.operator_token.type == T.BANG else T.INT
            if operand_type is None:
                return None
            if operand_type != expected:
                self.error(f"Tipo de operando inválido para '{expression.operator_token.lexeme}'", expression.operator_token)
                return None
            return expected
        if isinstance(expression, ast.Binary):
            left = self.analyze_expression(expression.left)
            right = self.analyze_expression(expression.right)
            if left is None or right is None:
                return None
            operator = expression.operator_token.type
            if operator in (T.EQUAL, T.NOT_EQUAL):
                valid = left == right
            else:
                valid = left == right == T.INT
            if not valid:
                self.error(f"Tipos de operandos inválidos para '{expression.operator_token.lexeme}'", expression.operator_token)
                return None
            return T.INT if operator in (T.PLUS, T.MINUS, T.STAR, T.SLASH) else T.BOOL
        raise TypeError(f"Expresión AST desconocida: {type(expression).__name__}")
