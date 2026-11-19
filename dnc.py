"""Command-line entry point for the DNC compiler."""

import argparse
from pathlib import Path

from lexer.dnc_lexer import Lexer


def main():
    """Read a UTF-8 source file from the command line and print its tokens."""
    parser = argparse.ArgumentParser(description="Print tokens from a DNC source file.")
    parser.add_argument("file", type=Path, help="path to the DNC source file")
    args = parser.parse_args()

    try:
        source = args.file.read_text(encoding="utf-8")
        lexer = Lexer(source)
        lexer.scan()
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f"{error}\n")

    for token in lexer.get_all_tokens():
        print(token)


if __name__ == "__main__":
    main()
