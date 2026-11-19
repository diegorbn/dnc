# Definitely Not C (DNC)

## Project Overview

Definitely Not C (DNC) is a small, C-like programming language and compiler developed as an educational project for a university course on programming language theory.

The compiler is written in Python and aims to translate `.dnc` source files into unoptimized x86-64 NASM assembly targeting Linux.

The goal is to understand and implement the fundamental stages of a compiler rather than build a production-ready language.

## Language Specification

The official grammar is located at:

`docs/dnc_ebnf.txt`

**Always consult this file before implementing or modifying the lexer, parser, or any language-related functionality.**

Treat the EBNF as the source of truth for the language's syntax. Do not introduce new keywords, operators, statements, or language features unless explicitly requested.

DNC uses `int mondongo() { ... }` as its mandatory entry point instead of the conventional `main()` function.

## Compiler Architecture

The compiler is designed around the following stages:

1. **Lexer:** Converts source code into tokens.
2. **Parser:** Uses recursive descent to validate syntax and construct an Abstract Syntax Tree (AST).
3. **Semantic analyzer:** Checks variable declarations, types, and scopes.
4. **Code generator:** Translates the validated AST into unoptimized x86-64 NASM assembly. NASM will take it from there.

Keep these stages logically separated and avoid duplicating responsibilities between them.

## Development Guidelines

- Use Python and its standard library whenever practical.
- Prefer simple, readable, and maintainable implementations over clever abstractions.
- Follow the existing project structure and naming conventions.
- Keep the compiler modular, with clearly defined responsibilities.
- Include meaningful tests for new functionality and edge cases.
- Provide clear error messages, including source locations when available.
- Avoid premature optimizations and unnecessary dependencies.
- Do not implement features beyond the agreed language specification.

## Educational Focus

The code should remain easy to understand, explain, and debug. Favor explicit logic and straightforward algorithms, especially in the lexer, parser, and semantic analyzer.

When a design decision introduces unnecessary complexity, prefer the simpler approach that satisfies the grammar and project requirements.