# Semantic analyzer algorithm

## Purpose, input and output

Parsing checks whether a program has the structure described by the grammar.
Semantic analysis checks whether that structure makes sense: names must be
accessible, declarations cannot conflict, and types must fit their uses. It
does not execute the program or store runtime values.

`SemanticAnalyzer.analyze(program)` receives the `Program` AST returned by the
parser. It returns `True` when no errors were found and `False` otherwise.
The analyzer's `errors` list contains `SemanticError` objects with a message
and the relevant source token. Calling `analyze` again clears the previous
errors and scopes.

## Data structures and scope operations

`scopes` is a list of dictionaries, ordered from outermost to innermost. Each
dictionary maps an identifier string to its declared type (`TokenType.INT` or
`TokenType.BOOL`). It contains no runtime values.

- `enter_scope()` appends an empty dictionary.
- `exit_scope()` pops the innermost dictionary.
- `declare(token, type)` checks the current dictionary, reports a duplicate
  if present, and otherwise inserts the type.
- `resolve(token)` searches the dictionaries in reverse order, returning the
  first type found, or reporting an undeclared variable and returning `None`.

Each AST block creates one scope, including the function body, each branch,
and each loop body. Nested shadowing is allowed. A declaration's initializer
is checked before the new name is inserted: a self-reference without an outer
declaration is invalid; when shadowing, the initializer can use the outer name.
The name is still registered after a faulty initializer so later uses do not
produce misleading undeclared-variable errors. A duplicate never replaces the
original declaration.

## Traversal and type checking

The analyzer walks statements in source order. A declaration checks for a
duplicate, analyzes its optional initializer, checks the type, then registers
the name if it is not a duplicate. An assignment resolves its target and
analyzes its value, requiring matching types. A `print` analyzes its expression
and accepts either type. An `if` or `while` analyzes its condition, requiring
`bool`, then analyzes each body block independently. Both branches are checked
regardless of the condition. A nested block is traversed as a block, without
adding any other implicit scopes.

Integer and boolean literals have types `int` and `bool`; identifiers get
their type from `resolve`. Unary `+` and `-` require and return `int`; `!`
requires and returns `bool`. Arithmetic `+`, `-`, `*`, `/` requires integers
and returns `int`. Ordering `<`, `<=`, `>`, `>=` requires integers and returns
`bool`. Equality `==` and `!=` accepts two operands of the same type and
returns `bool`. There are no implicit conversions. These are the chosen type
rules for the grammar, which describes syntax rather than operand types.

```text
analyze(program):
    clear errors and scopes
    analyze_block(program.body)
    return errors is empty

analyze_block(block):
    enter_scope()
    for statement in block.statements in order:
        analyze_statement(statement)
    exit_scope()  # also runs if traversal raises an exception

analyze_expression(expression):
    if literal: return its type
    if identifier: return resolve(identifier)
    recursively analyze operand(s)
    if any operand failed: return no type
    if operator does not accept the operand types: report error; return no type
    return the operator's result type
```

Errors are collected so independent problems can be reported together. A failed
expression returns no type, suppressing dependent type errors while allowing
other subexpressions and statements to be checked. Diagnostics include the
line and column from the relevant AST token. Unknown AST node kinds raise a
Python `TypeError`, since they indicate a compiler implementation error.

## Worked example

```c
int mondongo() {
    int x = 1;
    bool ready = true;
    if (ready) {
        int x = x + 1;
        print(x);
    }
    x = 2;
}
```

The function body opens the first scope. The tables show active scopes after
each significant step; entries are names and types, never values.

| Step | Outer scope | Inner scope |
| --- | --- | --- |
| Enter function block | empty | — |
| Declare `x` | `x: int` | — |
| Declare `ready` | `x: int`, `ready: bool` | — |
| Check `if (ready)` and enter its block | `x: int`, `ready: bool` | empty |
| Check initializer using outer `x`, then declare inner `x` | `x: int`, `ready: bool` | `x: int` |
| Check `print(x)` using inner `x` | `x: int`, `ready: bool` | `x: int` |
| Exit `if` block | `x: int`, `ready: bool` | — |
| Check `x = 2` using outer `x` | `x: int`, `ready: bool` | — |
| Exit function block | — | — |

## Invalid example

```c
int mondongo() {
    { int local = 1; }
    print(local);
}
```

After the inner block ends, its dictionary is popped. Resolving `local` in the
`print` searches the remaining function scope, finds no declaration, and
reports an undeclared variable at the identifier's line and column.

## Integration and limits

The optional CLI command `python3 dnc.py --check program.dnc` runs the lexer,
passes its tokens to the parser, and passes the AST directly to the analyzer.
It exits unsuccessfully for lexical, syntax, or semantic errors. The default
CLI remains a token viewer. There is no code generator yet; any future code
generator must only receive a program after `analyze` returns `True`.

The grammar contains no `for`, `break`, or `return` statements, so none are
analyzed. Empty blocks are valid. The analyzer does not check whether a
declared variable has been assigned before reading it, nor does it detect
runtime errors such as division by zero.
