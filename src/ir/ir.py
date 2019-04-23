"""
Methods and classes related to
Intermediate Representations of the Parse Tree.
"""

import json
from src.util import unique, CompilerMessage
import src.parser.grammar as grammar


def find(l, label):
    for index, ins in enumerate(l):
        if ins == ["break"]:
            l[index] = ["goto", label]

    return l


def readJson(name):
    """Read in JSON file"""

    try:
        with open(name, "r") as fileIn:
            lines = fileIn.read()
            # List of Lists
            prettyLines = json.loads(lines)
            currentNewBasicBlock = None
            currentFunctionBlocks = None
            ir = IR(None, None)
            for entry in prettyLines:
                command = entry[0]

                if command.startswith("."):
                    name = command[1:]
                    ir.ir[name] = {}
                    func = ir.ir[name]
                    func["blocks"] = []
                    args = entry[1]
                    func["arguments"] = args
                    func["declarations"] = entry[2]
                    currentFunctionBlocks = func

                elif command == "label":
                    instructions = []
                    label = entry[1]
                    new = BasicBlock(instructions, label)
                    currentNewBasicBlock = new
                    currentFunctionBlocks["blocks"].append(new)
                else:
                    currentNewBasicBlock.instructions.append(entry)

            return ir

    except FileNotFoundError:
        raise CompilerMessage("File cannot be read.")


class BasicBlock:
    """Defines a set of instructions and data that compose a Basic Block."""

    def __init__(self, instructions, label=None):
        self.instructions = instructions
        self.label = label
        self.instructions.insert(0, ["label", label])

    def print(self):
        """Print this basic block."""

        for i in self.instructions:
            print(i)
        print()


class IR:
    """Intermediate Representation class to hold IR data."""

    def __init__(self, parseTree, symbolTable):
        self.parseTree = parseTree
        self.symbolTable = symbolTable
        self.stack = []
        self.ir = {}
        self.current = None

    def generate(self):
        """Generate the IR from the parse tree."""

        self.parseTree.visit()
        self.visit(self.parseTree)

        return self.ir

    def closeBlock(self, erase=True):
        """Save the stack as a block and start a new block."""

        if self.stack:
            bb = BasicBlock(self.stack, unique.new("_L"))
            self.ir[self.current]["blocks"].append(bb)

        if erase:
            self.stack = []

    def visit(self, node):
        """Visit a node of the parse tree and recurse."""

        # Start new basic blocks when we first encounter certain nodes.
        if isinstance(node, grammar.FunctionDeclaration):
            # Start a new function entry
            self.ir[node.name] = {}
            self.ir[node.name]["blocks"] = []
            self.ir[node.name]["declarations"] = len(
                self.symbolTable.table[node.name]["variables"]
            )
            self.current = node.name
        elif isinstance(node, grammar.IfStatement):
            self.closeBlock()
        elif isinstance(node, grammar.ElseStatement):
            self.closeBlock()
        elif isinstance(node, grammar.LabelDeclaration):
            self.closeBlock()
        elif isinstance(node, grammar.Condition):
            self.closeBlock()
        elif isinstance(node, grammar.WhileStatement):
            self.closeBlock()
            node.savedLabel = unique.get("_L")
        elif isinstance(node, grammar.WhileCondition):
            self.closeBlock()

        # Slide to the left, slide to the right
        # Recurse recurse, recurse recurse!
        # ~ Dj Casper (Cha Cha Slide)
        if hasattr(node, "children"):
            for child in node.children:
                self.visit(child)
        elif isinstance(node, list):
            for child in node:
                self.visit(child)

        if not isinstance(node, list):
            # End the basic blocks we created earlier now that all
            # the node within have been visited.
            if isinstance(node, grammar.FunctionDeclaration):
                self.ir[node.name]["arguments"] = node.arguments.value
                self.closeBlock()
            elif isinstance(node, grammar.ReturnStatement):
                self.stack.append(node.ir())
                self.closeBlock()
            elif isinstance(node, grammar.IfBody):
                if node.hasElse:
                    self.stack.append(["goto", f"_L{unique.get('_L') + 3}"])
                self.closeBlock()
            elif isinstance(node, grammar.IfStatement):
                self.closeBlock()
            elif isinstance(node, grammar.Condition):
                i = [
                    "if",
                    node.value,
                    "GOTO",
                    f"_L{unique.get('_L') + 2}",
                    "else",
                    "GOTO",
                    f"_L{unique.get('_L') + 3}",
                ]
                self.stack.append(i)
                self.closeBlock()
            elif isinstance(node, grammar.ElseStatement):
                self.closeBlock()
            elif isinstance(node, grammar.LabelDeclaration):
                self.stack.insert(0, node.ir())
                self.closeBlock()
            elif isinstance(node, grammar.WhileStatement):
                # Must have a goto at the end of while statements to revisit the condition
                # The label of the condition is one after what was saved.
                self.stack.append(["goto", f"_L{node.savedLabel + 1}"])
                self.closeBlock()

                # breakLabel is the basic block that comes after the while statement
                breakLabel = f"_L{unique.get('_L') - node.savedLabel + 2}"

                # Replace the placeholder of the while condition with break label
                x = self.ir[self.current]["blocks"][node.savedLabel].instructions
                for index, ins in enumerate(x):
                    if ins[0] == "REPLACEME":
                        ins[-1] = breakLabel
                        x[index] = ins[1:]

                # Replace any break statements with a goto to the breakLabel
                for block in self.ir[self.current]["blocks"][node.savedLabel:]:
                    for index, ins in enumerate(block.instructions):
                        if ins == ["break"]:
                            block.instructions[index] = ["goto", breakLabel]

            elif isinstance(node, grammar.WhileCondition):
                self.stack.append(
                    [
                        "REPLACEME",
                        "if",
                        node.value,
                        "GOTO",
                        f"_L{unique.get('_L') + 2}",
                        "else",
                        "GOTO",
                        f"UNKNOWN",
                    ]
                )
                self.closeBlock()
            else:
                i = node.ir()
                if i is not None:
                    self.stack.append(i)

    def print(self):
        """Print the intermediate representation as a string."""

        print("```")
        for function in self.ir:
            print(f".{function} {self.ir[function]['arguments']}")
            print()  # Differentiate between basic blocks
            for block in self.ir[function]["blocks"]:
                block.print()
        print("```")

    def write(self, name):
        """Dump to JSON file"""

        s = []
        for function in self.ir:
            s.append(
                [
                    f".{function}",
                    self.ir[function]["arguments"],
                    len(self.symbolTable.table[function]["variables"]),
                ]
            )
            for block in self.ir[function]["blocks"]:
                for instruction in block.instructions:
                    s.append(instruction)
        print(s)
        with open(name, "w") as fileout:
            fileout.write(json.dumps(s))

    def __str__(self):
        s = []

        for function in self.ir:
            s.append(f".{function} ({self.ir[function]['arguments']})")
            for block in self.ir[function]["blocks"]:
                for line in block:
                    s.append(line)

        return "\n".join(s)
