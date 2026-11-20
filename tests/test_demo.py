import os
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path
from unittest.mock import patch

from lexer.dnc_lexer import Lexer
from lexer.token_type import TokenType
from parser import Parser
from semantic import SemanticAnalyzer


ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / 'demo' / 'samples'


def run_demo(module, *args):
    env = os.environ.copy()
    env['PYTHONPATH'] = os.pathsep.join(filter(None, (str(ROOT), env.get('PYTHONPATH'))))
    return subprocess.run([sys.executable, '-m', module, *map(str, args)], cwd=ROOT,
                          env=env, capture_output=True, text=True)


class DemoTests(unittest.TestCase):
    def test_lexer_table_matches_actual_tokens(self):
        lexer = Lexer((SAMPLES / 'valid.dnc').read_text(encoding='utf-8'))
        lexer.scan()
        result = run_demo('demo.lexer_demo', SAMPLES / 'valid.dnc')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line.split() for line in result.stdout.splitlines()
                if line.split() and line.split()[0].isdigit()]
        self.assertEqual(len(rows), len(lexer.tokens))
        for number, (row, token) in enumerate(zip(rows, lexer.tokens), 1):
            self.assertEqual(row, [str(number), token.type.name, repr(token.lexeme),
                                   str(token.line), str(token.column)])
        self.assertIn('incluye EOF', result.stdout)

    def test_lexer_runs_no_other_stages(self):
        from demo import lexer_demo
        with patch.object(sys, 'argv', ['lexer_demo', str(SAMPLES / 'valid.dnc')]), \
             patch('parser.Parser.parse_program', side_effect=AssertionError('parser invoked')), \
             patch.object(SemanticAnalyzer, 'analyze', side_effect=AssertionError('analyzer invoked')), \
             patch('sys.stdout'):
            self.assertEqual(lexer_demo.main(), 0)

    def test_errors_and_required_argument(self):
        result = run_demo('demo.lexer_demo', SAMPLES / 'lexical_error.dnc')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Carácter inesperado', result.stderr)
        self.assertIn('línea 2, columna 15', result.stderr)
        result = run_demo('demo.semantic_demo', SAMPLES / 'lexical_error.dnc')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Error lexico', result.stderr)
        for module in ('demo.lexer_demo', 'demo.semantic_demo'):
            self.assertEqual(run_demo(module).returncode, 2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'syntax.dnc'
            path.write_text('int mondongo() { print(1) }', encoding='utf-8')
            result = run_demo('demo.semantic_demo', path)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Error sintactico', result.stderr)
            result = run_demo('demo.lexer_demo', Path(directory) / 'missing.dnc')
            self.assertEqual(result.returncode, 1)
            self.assertIn('No se pudo leer', result.stderr)

    def test_semantic_examples(self):
        result = run_demo('demo.semantic_demo', SAMPLES / 'valid.dnc')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('SCOPE 0', result.stdout)
        self.assertIn('SCOPE 1', result.stdout)
        self.assertIn('z              int', result.stdout)
        self.assertNotIn('BUSCAR IDENTIFICADOR', result.stdout)
        self.assertNotIn('INT_LITERAL', result.stdout)
        result = run_demo('demo.semantic_demo', SAMPLES / 'semantic_error.dnc')
        self.assertEqual(result.returncode, 1)
        self.assertIn('SCOPE 1', result.stdout)
        self.assertIn("La variable 'local' no esta declarada", result.stdout)
        for arguments in ((SAMPLES / 'valid.dnc',), (SAMPLES / 'semantic_error.dnc',),
                          (SAMPLES / 'lexical_error.dnc',), ('--help',), ()):
            result = run_demo('demo.semantic_demo', *arguments)
            output = result.stdout + result.stderr
            self.assertFalse(any(unicodedata.combining(char)
                                 for char in unicodedata.normalize('NFD', output)))

    def test_scope_snapshots_and_behavior(self):
        lexer = Lexer('int mondongo() { int x = 1; { bool x = true; } { int y; } print(x); print(z); }')
        lexer.scan()
        program = Parser(lexer.get_all_tokens()).parse_program()
        snapshots = []
        traced = SemanticAnalyzer(on_scope_exit=lambda level, symbols: snapshots.append((level, symbols)))
        ordinary = SemanticAnalyzer()
        self.assertEqual(traced.analyze(program), ordinary.analyze(program))
        self.assertEqual(traced.errors, ordinary.errors)
        self.assertEqual(snapshots, [(1, {'x': TokenType.BOOL}),
                                     (1, {'y': TokenType.INT}),
                                     (0, {'x': TokenType.INT})])
        self.assertEqual(traced.scopes, [])
        traced.analyze(program)
        self.assertEqual(snapshots[0], (1, {'x': TokenType.BOOL}))


if __name__ == '__main__':
    unittest.main()
