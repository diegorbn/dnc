"""Mostrar los tokens reales producidos por el analizador léxico."""

import sys

from lexer.dnc_lexer import Lexer
from .formatting import arguments, heading, read_source, table


def main():
    args = arguments("Demostrar el análisis léxico de un archivo DNC.")
    heading("ANALIZADOR LÉXICO")
    print(f"Archivo: {args.archivo}\n")
    source = read_source(args.archivo)
    if source is None:
        return 1
    lexer = Lexer(source)
    error = None
    try:
        lexer.scan()
    except ValueError as exc:
        error = exc
    tokens = lexer.get_all_tokens()
    print("ANÁLISIS LÉXICO")
    table(("N.º", "Tipo", "Lexema", "Línea", "Columna"),
          ((i, token.type.name, repr(token.lexeme), token.line, token.column)
           for i, token in enumerate(tokens, 1)))
    print(f"\nTotal de tokens: {len(tokens)} (incluye EOF cuando se alcanza el final).")
    if error is not None:
        print(f"Error léxico: {error}", file=sys.stderr)
        return 1
    print("Análisis léxico completado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
