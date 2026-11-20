import unittest

from lexer.dnc_lexer import Lexer
from lexer.token_type import TokenType


class LexerTests(unittest.TestCase):
    def test_program_and_locations(self):
        lexer = Lexer('int mondongo() {\n  int if2=10; print(if2+1);\n}')
        lexer.scan()
        tokens = lexer.get_all_tokens()
        self.assertEqual([t.type for t in tokens], [
            TokenType.INT, TokenType.MONDONGO, TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE, TokenType.INT,
            TokenType.IDENT, TokenType.ASSIGN, TokenType.INT_LITERAL,
            TokenType.SEMICOLON, TokenType.PRINT, TokenType.LEFT_PAREN,
            TokenType.IDENT, TokenType.PLUS, TokenType.INT_LITERAL,
            TokenType.RIGHT_PAREN, TokenType.SEMICOLON, TokenType.RIGHT_BRACE,
            TokenType.EOF,
        ])
        self.assertEqual((tokens[6].lexeme, tokens[6].line, tokens[6].column), ('if2', 2, 7))

    def test_operators_and_keywords(self):
        lexer = Lexer('bool if else while print true false - * / == != ! < <= > >=')
        lexer.scan()
        self.assertEqual([t.type for t in lexer.get_all_tokens()], [
            TokenType.BOOL, TokenType.IF, TokenType.ELSE, TokenType.WHILE,
            TokenType.PRINT, TokenType.TRUE, TokenType.FALSE, TokenType.MINUS,
            TokenType.STAR, TokenType.SLASH, TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.BANG, TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER,
            TokenType.GREATER_EQUAL, TokenType.EOF,
        ])

    def test_empty_and_invalid(self):
        lexer = Lexer('')
        lexer.scan()
        self.assertEqual(lexer.get_all_tokens()[0].type, TokenType.EOF)
        with self.assertRaisesRegex(ValueError, 'línea 2, columna 1'):
            Lexer('\n@').scan()


if __name__ == '__main__':
    unittest.main()
