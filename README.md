# Definitely Not C

Definitely Not C (DNC) is an educational compiler project for a small C-like
language. Its grammar is defined in [docs/dnc_ebnf.txt](docs/dnc_ebnf.txt).
The current command-line entry point scans source text and prints its tokens.

## Usage

With Python 3, pass a UTF-8 encoded DNC source file as an argument:

```sh
python3 dnc.py program.dnc
```

The output includes each token's type, lexeme, and one-based starting line and
column, followed by an EOF token. An unrecognized character produces an error
with its location. The lexer recognizes tokens; it does not validate program
syntax.

To use the lexer from Python, create `Lexer(source)`, call `scan()`, and retrieve
the stored tokens with `get_all_tokens()`. Alternatively, `advance()` returns
one token without storing it; a subsequent `scan()` collects the remaining
tokens through EOF.

## Parser

The parser accepts the token list produced by the lexer and returns an abstract
syntax tree. It raises `ParserError` with a token location for syntax errors;
lexical errors remain `ValueError`s. The command-line entry point still prints
tokens.

```python
from lexer.dnc_lexer import Lexer
from parser import Parser

lexer = Lexer("int mondongo() { print(5 + 3 * 2); }")
lexer.scan()
program = Parser(lexer.get_all_tokens()).parse_program()
```

## Tests

```sh
python3 -m unittest discover -s tests
```
