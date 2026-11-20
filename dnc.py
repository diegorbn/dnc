"""Command-line entry point for the DNC compiler."""

import argparse
import sys
from pathlib import Path

from lexer.dnc_lexer import Lexer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer



class SpanishHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix="uso: ")


class SpanishArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: argumentos no válidos\n")


def main():
    """Read a UTF-8 source file from the command line and print its tokens."""
    parser = SpanishArgumentParser(
        description="Mostrar los tokens de un archivo fuente DNC.",
        usage="%(prog)s [-h] [--check] archivo",
        add_help=False,
        formatter_class=SpanishHelpFormatter,
    )
    parser._positionals.title = "argumentos posicionales"
    parser._optionals.title = "opciones"
    parser.add_argument("-h", "--help", action="help", help="mostrar esta ayuda y salir")
    parser.add_argument("--check", action="store_true", help="validar la sintaxis y la semántica")
    parser.add_argument("file", nargs="?", type=Path, metavar="archivo",
                        help="ruta del archivo fuente DNC")
    args, unknown = parser.parse_known_args()
    if unknown:
        parser.print_usage(sys.stderr)
        parser.exit(2, f"{parser.prog}: error: argumentos no reconocidos: {' '.join(unknown)}\n")
    if args.file is None:
        parser.print_usage(sys.stderr)
        parser.exit(2, f"{parser.prog}: error: falta el argumento obligatorio: archivo\n")

    try:
        source = args.file.read_text(encoding="utf-8")
        lexer = Lexer(source)
        lexer.scan()
    except OSError as error:
        parser.exit(1, f"No se pudo leer el archivo {args.file}: error del sistema {error.errno}\n")
    except UnicodeError:
        parser.exit(1, f"El archivo {args.file} no contiene texto UTF-8 válido\n")
    except ValueError as error:
        parser.exit(1, f"{error}\n")

    if args.check:
        try:
            program = Parser(lexer.get_all_tokens()).parse_program()
        except ParserError as error:
            parser.exit(1, f"{error}\n")
        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(program):
            parser.exit(1, "\n".join(str(error) for error in analyzer.errors) + "\n")
        return

    for token in lexer.get_all_tokens():
        print(f"Tipo: {token.type.name}, lexema: {token.lexeme!r}, "
              f"línea: {token.line}, columna: {token.column}")


if __name__ == "__main__":
    main()
