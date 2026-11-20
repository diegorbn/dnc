"""Mostrar las tablas del analizador semántico."""

import sys

from lexer.dnc_lexer import Lexer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer
from .formatting import arguments, heading, read_source, table, without_accents


def main():
    args = arguments("Mostrar las tablas de simbolos de un archivo DNC.", unaccented=True)
    heading("ANALIZADOR SEMANTICO")
    print(f"Archivo: {args.archivo}")
    source = read_source(args.archivo, unaccented=True)
    if source is None:
        return 1
    lexer = Lexer(source)
    try:
        lexer.scan()
    except ValueError as error:
        print(f"Error lexico: {without_accents(error)}", file=sys.stderr)
        return 1
    try:
        program = Parser(lexer.get_all_tokens()).parse_program()
    except ParserError as error:
        print(f"Error sintactico: {without_accents(error)}", file=sys.stderr)
        return 1

    completed_scopes = []
    analyzer = SemanticAnalyzer(on_scope_exit=lambda level, symbols: completed_scopes.append((level, symbols)))
    success = analyzer.analyze(program)
    print("\nTABLAS DE SIMBOLOS")
    for level, symbols in completed_scopes:
        print(f"\nSCOPE {level}")
        if symbols:
            table(("Identificador", "Tipo"),
                  ((name, kind.name.lower()) for name, kind in symbols.items()))
        else:
            print("(sin variables)")
    if not success:
        for error in analyzer.errors:
            print(f"\nError semantico: {without_accents(error)}")
        return 1
    print("\nAnalisis semantico completado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
