import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, 'dnc.py', *arguments],
                              text=True, capture_output=True)

    def test_help_and_missing_argument(self):
        help_result = self.run_cli('--help')
        self.assertEqual(help_result.returncode, 0)
        self.assertIn('argumentos posicionales', help_result.stdout)
        self.assertIn('mostrar esta ayuda', help_result.stdout)
        missing = self.run_cli()
        self.assertEqual(missing.returncode, 2)
        self.assertIn('falta el argumento obligatorio', missing.stderr)

    def test_tokens_and_lexical_error(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'test.dnc'
            source.write_text('int @', encoding='utf-8')
            invalid = self.run_cli(str(source))
            self.assertEqual(invalid.returncode, 1)
            self.assertIn('Carácter inesperado', invalid.stderr)
            self.assertIn('línea 1, columna 5', invalid.stderr)
            source.write_text('int', encoding='utf-8')
            valid = self.run_cli(str(source))
            self.assertEqual(valid.returncode, 0)
            self.assertIn("Tipo: INT, lexema: 'int', línea: 1, columna: 1", valid.stdout)


if __name__ == '__main__':
    unittest.main()
