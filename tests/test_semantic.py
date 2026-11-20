import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lexer.dnc_lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def analyze(body):
    lexer = Lexer('int mondongo() {' + body + '}')
    lexer.scan()
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(Parser(lexer.get_all_tokens()).parse_program())
    return success, analyzer


class SemanticTests(unittest.TestCase):
    def test_valid_scopes_and_control_flow(self):
        success, analyzer = analyze('''
            int x = 1; bool b = true;
            { int x = x + 1; { x = -x; print(b); } }
            if (x < 2) { bool b = false; print(b == false); }
            else { print(x); }
            while (!b) { x = x / 2; b = x != 0; }
            {}''')
        self.assertTrue(success, analyzer.errors)
        self.assertEqual(analyzer.scopes, [])
        self.assertTrue(analyze('')[0])

    def test_declarations_and_scope_errors(self):
        success, analyzer = analyze('''
            int self = self; int x; int x;
            { int local; } print(local); missing = x;
        ''')
        self.assertFalse(success)
        self.assertEqual(len(analyzer.errors), 4)
        messages = [str(error) for error in analyzer.errors]
        self.assertIn("'self' no está declarada", messages[0])
        self.assertIn("'x' ya está declarada", messages[1])
        self.assertIn("'local' no está declarada", messages[2])
        self.assertIn("'missing' no está declarada", messages[3])
        self.assertIn('línea 2, columna', messages[0])

    def test_type_errors_and_no_cascades(self):
        success, analyzer = analyze('''
            int x = true; bool b = 1; x = b;
            print(true + 1); print(!1); print(-false);
            print(1 == true); print(true < false);
            if (1) {} while (x + missing) {}
        ''')
        self.assertFalse(success)
        self.assertEqual(len(analyzer.errors), 10)
        self.assertEqual(sum('condición' in str(error) for error in analyzer.errors), 1)
        self.assertTrue(any("'missing' no está declarada" in str(error) for error in analyzer.errors))

    def test_analyzer_can_be_reused(self):
        _, analyzer = analyze('print(missing);')
        lexer = Lexer('int mondongo() {}')
        lexer.scan()
        self.assertTrue(analyzer.analyze(Parser(lexer.get_all_tokens()).parse_program()))
        self.assertEqual(analyzer.errors, [])

    def test_cli_check(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.dnc'
            for code, expected, diagnostic in [
                ('int mondongo() { int x = 1; }', 0, ''),
                ('int mondongo() { print(x); }', 1, "'x' no está declarada"),
                ('int mondongo() { print(1) }', 1, 'Se esperaba SEMICOLON'),
                ('int mondongo() { @ }', 1, 'Carácter inesperado'),
            ]:
                with self.subTest(code=code):
                    source.write_text(code, encoding='utf-8')
                    result = subprocess.run([sys.executable, 'dnc.py', '--check', str(source)],
                                            text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected)
                    self.assertIn(diagnostic, result.stderr)


if __name__ == '__main__':
    unittest.main()
