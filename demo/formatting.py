"""Formato compartido y argumentos de las demostraciones."""

import argparse
import sys
import unicodedata
from pathlib import Path


class SpanishHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix="uso: ")


class SpanishArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        message = "argumentos no validos" if getattr(self, "unaccented", False) else "argumentos no válidos"
        self.exit(2, f"{self.prog}: error: {message}\n")


def arguments(description, unaccented=False):
    parser = SpanishArgumentParser(description=description, add_help=False,
                                   formatter_class=SpanishHelpFormatter)
    parser.unaccented = unaccented
    parser._positionals.title = "argumentos posicionales"
    parser._optionals.title = "opciones"
    parser.add_argument("-h", "--help", action="help", help="mostrar esta ayuda y salir")
    parser.add_argument("archivo", type=Path, help="archivo fuente DNC")
    return parser.parse_args()


def without_accents(text):
    return ''.join(char for char in unicodedata.normalize('NFD', str(text))
                   if not unicodedata.combining(char))


def read_source(path, unaccented=False):
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        message = f"No se pudo leer el archivo {path}: error del sistema {error.errno}"
    except UnicodeError:
        message = f"El archivo {path} no contiene texto UTF-8 válido"
    print(without_accents(message) if unaccented else message, file=sys.stderr)
    return None


def heading(title):
    print(f"\n========== {title} ==========\n")


def table(headers, rows):
    rows = [tuple(str(value) for value in row) for row in rows]
    widths = [max(len(str(header)), *(len(row[i]) for row in rows)) if rows
              else len(str(header)) for i, header in enumerate(headers)]
    def line(row):
        return "  ".join(str(value).ljust(width) for value, width in zip(row, widths)).rstrip()
    print(line(headers))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(line(row))


