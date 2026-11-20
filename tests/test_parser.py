import unittest

from lexer.dnc_lexer import Lexer
from lexer.token_type import TokenType as T
from parser import Parser, ParserError
from parser import ast


def parse(source):
    lexer = Lexer(source)
    lexer.scan()
    return Parser(lexer.get_all_tokens()).parse_program()


class ParserTests(unittest.TestCase):
    def test_empty_and_statements(self):
        self.assertEqual(parse('int mondongo() {}').body.statements, [])
        program = parse('''int mondongo() {
            int x; bool b = true; x = -2;
            if (b) { print(x); } else { { x = +1; } }
            while (!false) { x = x - 1; }
        }''')
        statements = program.body.statements
        self.assertEqual([type(s) for s in statements], [
            ast.Declaration, ast.Declaration, ast.Assignment, ast.If, ast.While])
        self.assertIsNone(statements[0].initializer)
        self.assertIsInstance(statements[1].initializer, ast.BoolLiteral)
        self.assertIsInstance(statements[3].else_block.statements[0], ast.Block)
        self.assertIsInstance(statements[4].condition, ast.Unary)

    def test_precedence_and_associativity(self):
        body = parse('int mondongo() { print(5 + 3 * 2); print((5 + 3) * 2); print(9 - 3 - 1); }').body
        first, second, third = [s.value for s in body.statements]
        self.assertEqual(first.operator_token.type, T.PLUS)
        self.assertEqual(first.right.operator_token.type, T.STAR)
        self.assertEqual(second.operator_token.type, T.STAR)
        self.assertEqual(second.left.operator_token.type, T.PLUS)
        self.assertEqual(third.left.operator_token.type, T.MINUS)
        self.assertIsInstance(third.right, ast.IntLiteral)

    def test_all_comparisons_and_unary(self):
        for op in ('==', '!=', '<', '<=', '>', '>='):
            with self.subTest(op=op):
                expression = parse(f'int mondongo() {{ print(!-+x {op} 2 / 1); }}').body.statements[0].value
                self.assertEqual(expression.operator_token.lexeme, op)
                self.assertEqual(expression.left.operand.operand.operator_token.type, T.PLUS)
                self.assertEqual(expression.right.operator_token.type, T.SLASH)

    def test_invalid_programs(self):
        cases = [
            'int main() {}', 'bool mondongo() {}', 'int mondongo(1) {}',
            'int mondongo() {} int', 'int mondongo() {',
            'int mondongo() { int x }', 'int mondongo() { x; }',
            'int mondongo() { print(1 + ); }', 'int mondongo() { print(1 < 2 < 3); }',
            'int mondongo() { if (true) print(1); }',
            'int mondongo() { while (true) {} else {} }',
            'int mondongo() { ; }',
        ]
        for source in cases:
            with self.subTest(source=source), self.assertRaises(ParserError):
                parse(source)

    def test_error_location_and_eof(self):
        with self.assertRaises(ParserError) as caught:
            parse('int mondongo() {\n print(1 + );\n}')
        self.assertEqual((caught.exception.token.type, caught.exception.token.line,
                          caught.exception.token.column), (T.RIGHT_PAREN, 2, 12))
        self.assertIn('línea 2, columna 12', str(caught.exception))
        with self.assertRaises(ParserError) as caught:
            parse('int mondongo() {')
        self.assertEqual(caught.exception.token.type, T.EOF)
        self.assertIn('RIGHT_BRACE', str(caught.exception))

    def test_navigation_and_token_list_invariant(self):
        lexer = Lexer('')
        lexer.scan()
        parser = Parser(lexer.get_all_tokens())
        self.assertEqual(parser.advance().type, T.EOF)
        self.assertTrue(parser.check(T.EOF))
        self.assertEqual(parser.expect(T.EOF), parser.peek())
        with self.assertRaises(ValueError):
            Parser([])
        with self.assertRaises(ValueError):
            Parser(lexer.get_all_tokens() * 2)


if __name__ == '__main__':
    unittest.main()
