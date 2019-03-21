# pylint: disable=missing-docstring

"""
Classes that represent grammar rules for our Parse Tree.
"""

count = {"none": 0}


def unique(prefix=None):
    """Generate a new, unique variable name with optional prefix."""

    if prefix:
        if prefix not in count:
            count[prefix] = 0
        count[prefix] += 1
        return f"{prefix}{count[prefix]}"

    count["none"] += 1
    return f"r{count['none']}"


def generateIr(parseTree):
    """Generate an intermediate representation from a parse tree."""

    ir = []
    visitChildren(parseTree, ir)
    return ir


def visitChildren(node, ir):
    """Visit each node of the parse tree."""

    if isinstance(node, FunctionDeclaration):
        ir.append(node.ir())

    if hasattr(node, "children"):
        for child in node.children:
            visitChildren(child, ir)
    elif isinstance(node, list):
        for child in node:
            visitChildren(child, ir)

    if not isinstance(node, list):
        if not isinstance(node, FunctionDeclaration):
            i = node.ir()
            if i is not None and not i.isdigit():
                ir.append(i)


def parseToken(desc, content="", children=[]):
    """Parse a token into the relevant class."""

    # Check if the node is a terminal
    if desc in terminals:
        return terminals[desc](content)

    # Check if the node exists
    if desc in nodes:
        return nodes[desc](children)

    # Did not match any of the known parse tree nodes.
    # Classify it as a "general"  node
    return None


def printPrefix(level):
    """Print a prefix level deep for pretty printing."""

    for _ in range(level):
        print("  ", end=" ")
    print("| - ", end=" ")


class Node:
    """General parse tree node class"""

    def __init__(self, *children):
        if len(children) == 1:
            self.children = children[0]
        else:
            self.children = children

    def __str__(self):
        return self.__class__.__name__

    def print(self, level=0):
        """
        General node print method.
        First, print the class name, then print all its children.

        This method is overriden at lower level nodes like ConstNum.
        """

        printPrefix(level)
        print(self.__class__.__name__)

        if isinstance(self.children, list):
            for child in self.children:
                child.print(level + 1)
        else:
            for child in self.children[0]:
                child.print(level + 1)

    def ir(self, intermediate=False):
        return None


# Parse Tree Node Classes


class Program(Node):
    pass


class DeclarationList(Node):
    pass


class Declaration(Node):
    pass


class FunctionDeclaration(Declaration):
    def __init__(self, *children):
        self.children = children
        # self.type = children[0][0].value
        self.name = children[0][1].value

    def ir(self):
        return f".{self.name} ()"


class StatementList(Node):
    pass


class Statement(Node):
    pass


class ReturnStatement(Statement):
    def ir(self):
        # Return the most recently assigned variable
        return f"ret r{count['none']}"


class VariableDeclaration(Declaration):
    def __init__(self, *children):
        self.children = children
        self.type = children[0][0].value
        self.name = children[0][1].value

    def ir(self):
        return f"{self.name} = null"


# Assignments


class VariableAssignment(Declaration):
    def __init__(self, *children):
        self.children = children
        self.name = children[0][0].value

    def ir(self):
        recent = count["none"]
        return f"{self.name} = r{recent}"


class IncrementAssignment(VariableAssignment):
    def __init__(self, *children):
        self.children = children
        self.name = children[0][0].value

    def ir(self):
        return f"{self.name} = {self.name} + 1"


class DecrementAssignment(VariableAssignment):
    def __init__(self, *children):
        self.children = children
        self.name = children[0][0].value

    def ir(self):
        return f"{self.name} = {self.name} - 1"


class PlusEqualAssignment(VariableAssignment):
    def __init__(self, *children):
        self.children = children

        print(children[0])


class MinusEqualAssignment(VariableAssignment):
    pass


# Expressions


class Expression(Node):
    pass


class AdditionExpression(Expression):
    def ir(self):
        var = unique()
        return f"{var} = {self.children[0].ir(True)} + {self.children[1].ir(True)}"


class SubtractionExpression(Expression):
    def ir(self):
        var = unique()
        return f"{var} = {self.children[0].ir(True)} - {self.children[1].ir(True)}"


class MultiplicationExpression(Expression):
    def ir(self):
        var = unique()
        return f"{var} = {self.children[0].ir(True)} * {self.children[1].ir(True)}"


class DivisionExpression(Expression):
    def ir(self):
        var = unique()
        return f"{var} = {self.children[0].ir(True)} / {self.children[1].ir(True)}"


class ModulusExpression(Expression):
    def ir(self):
        var = unique()
        return f"{var} = {self.children[0].ir(True)} % {self.children[1].ir(True)}"


class BooleanAnd(Expression):
    pass


class BooleanOr(Expression):
    pass


class LTOEExpression(Expression):
    pass


class GTOEExpression(Expression):
    pass


class LTExpression(Expression):
    pass


class GTExpression(Expression):
    pass


class NotEqualExpression(Expression):
    pass


class EqualExpression(Expression):
    pass


# Statements


class ForStatement(Statement):
    pass


class IncludeStatement(Statement):
    pass


class CallStatement(Statement):
    pass


class IfStatement(Statement):
    pass


class ElseStatement(Statement):
    pass


# A dictionary of all the parse tree nodes we recognize
# Key: string of the grammar rule
# Value: the associated class

nodes = {
    "program": Program,
    "declarationList": DeclarationList,
    "declaration": Declaration,
    "varDec": VariableDeclaration,
    "assignment": VariableAssignment,
    "incAssignment": IncrementAssignment,
    "decAssignemnt": DecrementAssignment,
    "incEqualAssignment": PlusEqualAssignment,
    "decEqualAssignment": MinusEqualAssignment,
    "functionDeclaration": FunctionDeclaration,
    "statementList": StatementList,
    "statement": Statement,
    "returnStatement": ReturnStatement,
    "forStatement": ForStatement,
    "includeStatement": IncludeStatement,
    "callStatement": CallStatement,
    "ifStatement": IfStatement,
    "elseStatement": ElseStatement,
    "expression": Expression,
    "addExpr": AdditionExpression,
    "subExpr": SubtractionExpression,
    "multExpr": MultiplicationExpression,
    "divExpr": DivisionExpression,
    "modExpr": ModulusExpression,
    "boolAnd": BooleanAnd,
    "boolOr": BooleanOr,
    "lteExpr": LTOEExpression,
    "gteExpr": GTOEExpression,
    "ltExpr": LTExpression,
    "gtExpr": GTExpression,
    "neExpr": NotEqualExpression,
    "eExpr": EqualExpression,
}

# General Node fallback
class GeneralNode(Node):
    """General node (fallback)."""

    def __init__(self, value, children=[]):
        self.value = value
        self.children = children

    def print(self, level=0):
        # if len(self.children) == 0:
        #    printPrefix(level)
        #    print(self.value)
        # else:
        for child in self.children:
            child.print(level)


# Terminal Nodes


class TypeSpecifier(Node):
    """Type specifier node."""

    def __init__(self, value):
        self.value = value

    def print(self, level=0):
        printPrefix(level)
        print(f"{self.__class__.__name__}: {self.value}")


class ConstNum(Node):
    """Number constant node."""

    def __init__(self, value):
        self.value = value

    def print(self, level=0):
        printPrefix(level)
        print(f"{self.__class__.__name__}: {self.value}")

    def ir(self, intermediate=False):
        if intermediate:
            return self.value

        return None


class Identifier(Node):
    """ID node."""

    def __init__(self, value):
        self.value = value

    def print(self, level=0):
        printPrefix(level)
        print(f"{self.__class__.__name__}: {self.value}")

    def ir(self, intermediate=False):
        if intermediate:
            return self.value

        return None


class Filename(Node):
    """Filename node."""

    def __init__(self, value):
        self.value = value

    def print(self, level=0):
        printPrefix(level)
        print(f"{self.__class__.__name__}: {self.value}")

    def ir(self, intermediate=False):
        if intermediate:
            return self.value

        return None


class String(Node):
    """String node."""

    def __init__(self, value):
        self.value = value

    def print(self, level=0):
        printPrefix(level)
        print(f"{self.__class__.__name__}: {self.value}")

    def ir(self, intermediate=False):
        if intermediate:
            return self.value

        return None


# A dictionary of all the terminal parse tree nodes we recognize
# Key: string of the grammar rule
# Value: the associated class

terminals = {
    "typeSpecifier": TypeSpecifier,
    "ID": Identifier,
    "constNum": ConstNum,
    "fileName": Filename,
    "str": String,
}
