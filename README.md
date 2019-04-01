# Compiler in Python: Design Document

Group Members: Charles Hermann, Izeah Olguin, Paco Coursey

Last Updated: 03/31/2019

## Quickstart

Clone the repository:

```bash
$ git clone https://github.com/pacocoursey/compiler.git
```

Install the dependencies using [pip3](https://pypi.org/project/pip/):

```bash
$ make install
```

## Overview

Our Python compiler currently meets the standards expected of the second
deliverable.

Our scanner reads in a file as a string of characters and produces a list of labeled tokens. These tokens become acquired by the parser and produce an abstract representation.

We then generate our parse tree, utilizing the list of labeled tokens -- and a recursive function, flattenTree
which is our implementation of a DFS tree traversal algorithm. This allows us to develop our parse tree structure of parent/children nodes given a collapsable grammar rule.

Once the parse tree has been created:

We are able to employ its structure and data into creating the symbol table. Again, we focused on the DFS tree traversal algorithm by visiting each parent node and traversing to each of its children. With this recursive method, we are able to visualize our scope within the tree, and confidently update the tree after each visit to every node.  

Furthermore, we extend this structure to design our Intermediate Representation and exploit the visitChildren function to return our IR as a list of strings. Reading in an IR instead of a source file, as well as writing out the IR to a file with a specified name have also been developed.

As a group, we have met numerous times to discuss our design, implementation and overall expectations of our compiler, which has lead to overcoming numerous amounts of errors and feats against our design endeavors.

As mentioned during the code review in class, our Python code is a bit extensive, however this contributes to the readability and allows our software to be more dynamic.

## Usage

Our compiler uses Python 3.

### Character Count

This program returns the number of characters found in a given file. Run using:

```bash
$ python3 src/character_count.py FILENAME
```

### Scanner

The scanner tokenizes a C program and returns a list of the known tokens. Run using:

```bash
$ python3 src/main.py -s samples/plain.c
```

### Parser

The parser converts a list of tokens generated by the scanner and constructs an abstract representation of the program using a pre-defined C grammar. Run using:

```bash
$ make main
# or
$ python3 src/main.py -s -p samples/plain.c
```

### Symbol Table

The symbol table uses the parse tree construction and a recursive structure to visit each node and retain its current scope
Run Using:

```bash
$ make main
# or
$ python3 src/main.py -t samples/plain.c
```

### Intermediate Representation

The IR uses the parse tree construction and exploits recursion (visitChildren function) to return our IR as a list of strings.
Run Using:

```bash
$ make main
# or
$ python3 src/main.py -r samples/plain.c
```

To read in an IR, instead of source file, Run Using:

```bash
$ make main
# or
$ python3 src/main.py -ri tmp.txt
```

To write out the IR to a file with a specified name, Run Using:

```bash
$ make main
# or
$ python3 src/main.py -ro foo.txt samples/plain.c
```

## Design Discussion

### Scanner Implementation

Our scanner parses characters in a 'chunk', with a start an and end counter. We iterate through the chunk to match our tokens in the following order: Symbols, Operators, Keywords, Identifiers and Numbers.

We are not focused on speed, which is why we opted not to use regular expressions. This gives us more logical control over what tokens we recognize, and it is easier to handle edge cases like multi-line comments.

### Parser Implementation

Currently, we have implemented seven classes. Each of which is a static parse method. These classes are defined within `grammar.py`. 'grammar.py', also contains our list of rules, which we currently recognize.

The `paser.py` file design is similar to that of Nora Sandler's design. We employ a recursive descent parsing algorithm, which pushes elements onto a stack from right to left. Finally, we then shift, reduce and repeat.

In the rules of `grammar.py`, we attempt to break as early as possible to avoid checking more tokens than we have to. This helps speed up the rule searching.

### Symbol Table Implementation

### IR Implementation

### Limitations

- Large code base
- Complex logic on rule specification

### Benefits

- Few files, things can be modified quickly
- Design and hierarchy is well established
- Good separation of concepts into modularized files

## Scanner Specification

Tokens that we currently recognize:

- [X] Identifiers
- [X] Numbers (ints, floats)
- [X] Block symbols `(, ), {, }, [, ]`
- [X] Unary operators `&, |, ^, ~`
- [X] Equality operators `<, >, <=, >=, ==, !=`
- [X] Assignment operators `=, +=, -=, *=, /=, ++, --`
- [X] Strings `"", ''`
- [X] Misc tokens `,, ., ;, \\, ->, #`
- [X] Sum operators `+, -`
- [X] Multiplication operators `*, /, %`
- [X] Boolean operators `&&, ||, !, <<, >>`
- [X] Number type keywords `int, long, double, short, signed, unsigned, float`
- [X] Data type keywords `struct, enum, union, record`
- [X] Flow control keywords `if, else, while, for, break, continue, return`
- [X] Boolean keywords `true, false`
- [X] Misc keywords `static, sizeof, typedef, const, extern, auto`

## Grammar Specification

High level AST nodes that we currently recognize:

- [X] Program
- [X] Function Declaration
- [X] Type Specifier: int, float
- [X] Return Statement
- [X] Number Constant: int, float
- [X] Identifiers
- [X] Variable Declaration
- [X] If/Else Control Flow
- [X] For Statements
- [X] Expressions
- [X] Assignments (+=, -=, +=, --, etc)

AST nodes that we will recognize in the next few weeks:

- [ ] While Loops
- [ ] Function Calls

## Class-defined Specifications

Features required in our implementation.

- [ ] Functions
- [ ] Return
- [ ] Break
- [ ] Variables
- [ ] Arithmetic (+, -, *,)
- [ ] Assignment
- [ ] Boolean Expressions
- [ ] Goto
- [ ] If
- [ ] While
- [ ] Unary Operators
- [ ] Integers (default, signed, syslen)

### Extra Features

Extra features for bonus points.

- [ ] `char`, `float`
- [ ] For
- [ ] Switch
- [ ] Binary Operators (&, |, ^)
- [ ] Assignment Helpers (+=, -=, *=, /=, ++, --)

### Out of Bound Features

Extremely extra features.

- Pointers
- Arrays
- Compiler Preprocessing (macros, #include)
- Struct
- Enum
- Library Calls
- Casting
- Promotion
- Strings
- Type Specs

## Code Style

Formatted using [Black](https://github.com/ambv/black).
Linted using [PyLint](https://www.pylint.org/).

## Related

- [SmallerC](https://github.com/alexfru/smallerc)
- [Tiny C Compiler](https://bellard.org/tcc/)
