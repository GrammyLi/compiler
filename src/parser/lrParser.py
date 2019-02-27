"""
The main parsing module.
Reads in the grammar and generated action and goto tables.
Parses the list of tokens using the action and goto tables.
"""


import logging
import sys
import os
import json
import parser.grammar as grammar
from util import readFile

debug = True


class LRParser:
    """The general parser class."""

    def __init__(self):
        # Rules parsed from grammar
        self.rules = {}

        # Nessisary variables to generate acion and goto tables
        self.itemSets = {}
        self.transitions = {}
        self.setNum = 0
        self.terminals = []
        self.nonTerminals = []

        # Action and goto tables
        self.actions = {}
        self.goto = {}

        # Parse tree, represented as a node list
        self.parseTree = []

    def buildTables(self):
        """Build the item sets, transitions, and action goto tables."""

        # Start itemset 0 with the accepting state
        self.itemSets[0] = [Item("ACC", "program", 0, "$")]

        # close Itemsets and create new sets until no more
        i = 0
        while i <= max(self.itemSets.keys()):
            if self.hasItemSet(i):
                # close out itemset i
                self.closure(i)
                # change nonterminal followers to terminals in itemset i
                self.cleanItemSet(i)
                # create any new itemsets from itemset i
                self.createItemSets(i)
                # search through itemsets and remove any copies
                self.cleanItemSets()
            i = i + 1

        # build tables
        self.buildActionGoto()

        # Save this for testing!
        # if debug:
        #     self.printRules()
        #     self.printItemSets()
        #     self.printTransitions()
        #     self.printTable()

    def parseGrammar(self, grammarText):
        """
        Parse the input grammar into rules.
        The variable self.rules is filled here.
        self.rules is a dictionary with the LHS of a rule as the key,
        and lists as the value. The lists are the different RHS' that
        the rule points to.
        """

        # Augment rules with accepting state
        self.rules["ACC"] = [["program"]]

        # Open file with grammar
        lines = grammarText.splitlines()

        # parse grammar file into rules
        for line in lines:
            if line == "":
                # Skip blank lines
                continue
            elif line[0] == "#":
                # Skip comment lines
                continue

            rule = line.split(" ")
            # Check to see if valid format
            if rule[1] == "->":
                # seperate the "|" out of the rule
                last = 2
                for i, r in enumerate(rule):
                    if r == "|":
                        # if lhs of rule is in self.rules, append rhs of rule to the list
                        if rule[0] in self.rules.keys():
                            self.rules[rule[0]].append(rule[last:i])
                        # if lhs of rule is not in self.rules, add new dictionary element
                        else:
                            self.rules[rule[0]] = [rule[last:i]]
                        last = i + 1
                # for loop above catches all but the last rule from the grammar
                # this if-else is to catch that final rule
                if rule[0] in self.rules.keys():
                    self.rules[rule[0]].append(rule[last:])
                else:
                    self.rules[rule[0]] = [rule[last:]]

        # add all the nonTerminals to self.nonTerminal list
        for k in self.rules:
            if k not in self.nonTerminals:
                self.nonTerminals.append(k)

        # add all the terminals to the self.terminals list
        for v in self.rules.values():
            for tokenList in v:
                for token in tokenList:
                    if token not in self.nonTerminals and token not in self.terminals:
                        self.terminals.append(token)

    def closure(self, setNum):
        """
        Close out an item set.
        This involves expanding out rules from the grammar.
        """

        if debug:
            logging.debug("Closing out itemset %s", setNum)
        # newSet is just the itemset we are currently interested in
        newSet = self.itemSets[setNum]
        done = False

        # keep looping until no more rules can be expanded
        while not done:
            # for each item in the set:
            for currItem in newSet:
                new = False
                # get the token after the dot
                a = currItem.getRightAfter()
                # get all the tokens after the token after the dot
                b = currItem.getAfter()
                # following becomes the first token after the token after the seperator
                # if there is a token after the token after the seperator
                # if not, following is just the o
                following = currItem.following
                if b:
                    following = b[0]
                # if a is a nonTerminal, expand rule
                if a in self.rules.keys():
                    new = True
                    # for each rule for nonTerminal a:
                    for rule in self.rules[a]:
                        # make a new item for nonTerminal a rule
                        rhs = " ".join(rule)
                        newItem = Item(a, rhs, 0, following)
                        # check if item already exists in the itemSet
                        isNew = True
                        for tempItem in newSet:
                            if newItem.isSame(tempItem):
                                isNew = False
                        # if item is new then add it to set
                        if isNew:
                            newSet.append(newItem)
                            new = True
                # if no new items found we are done
                if not new:
                    done = True

    def cleanItemSet(self, setNum):
        """Remove any nonterm following token from item set."""

        nonTerms = True
        # loop until no more nonTerminal following tokens found in itemset
        while nonTerms:
            nonTerms = False
            for itemNum in range(len(self.itemSets[setNum])):
                # if item.following in itemSet is a nonTerm then expand the nonTerm into terminal
                if self.itemSets[setNum][itemNum].following in self.nonTerminals:
                    nonTerms = True
                    lhs = self.itemSets[setNum][itemNum].lhs
                    rhs = self.itemSets[setNum][itemNum].rhs
                    sep = self.itemSets[setNum][itemNum].seperator
                    following = self.itemSets[setNum][itemNum].following
                    # for each rule the nonTerminal token expands into:
                    for numRule in range(len(self.rules[following])):
                        newItem = Item(lhs, rhs, sep, self.rules[following][numRule][0])
                        # check to see if new item is new to the set
                        isNew = True
                        for tempItem in self.itemSets[setNum]:
                            if newItem.isSame(tempItem):
                                isNew = False
                        # if it is, add it to the itemSet
                        if isNew:
                            self.itemSets[setNum].append(newItem)
                    # delete the old rule with the nonTerminal following token
                    del self.itemSets[setNum][itemNum]
                    break

    def createItemSets(self, setNum):
        """
        Create new item sets from past item sets.
        This is tracked with the transition table.
        """

        # for each item in itemSet[setNum]
        for currItem in self.itemSets[setNum]:
            # make a newItem from the currItem with the seperator incremented by 1
            newItem = currItem.incSeperator()
            # get the delimeter for the transition table
            delimeter = newItem.getRightBefore()
            # if delimeter exists
            if delimeter:
                # if the transitions for itemSet[setNum] does not exist add it
                if setNum not in self.transitions.keys():
                    self.transitions[setNum] = {}
                # if delimeter does not exist in transition[setNum],
                # add it and increment self.setNum by 1
                if delimeter not in self.transitions[setNum].keys():
                    self.setNum = self.setNum + 1
                    self.transitions[setNum][delimeter] = self.setNum
                # if the new itemSet does not exist in self.itemSets add it
                if self.transitions[setNum][delimeter] not in self.itemSets.keys():
                    self.itemSets[self.transitions[setNum][delimeter]] = []
                # add the newItem to the new set
                self.itemSets[self.transitions[setNum][delimeter]].append(newItem)

    def cleanItemSets(self):
        """Clean item sets of any identical sets."""

        # compare the itemSets backwards
        # So compare every set with the sets that came before it
        for i in range(self.setNum, -1, -1):
            for j in range(i - 1, -1, -1):
                # compare set i with set j
                same = True
                for itemSet in self.itemSets[j]:
                    inThere = False
                    for itemSetCheck in self.itemSets[i]:
                        if itemSetCheck.isSame(itemSet):
                            inThere = True
                    if not inThere:
                        same = False
                        break
                # if itemSets i and j are identical delete itemSet i (the itemSet that came later)
                if same:
                    if debug:
                        logging.debug("Replacing itemset %s with itemset %s", i, j)
                    del self.itemSets[i]
                    # self.setNum is now the lowest available set number
                    self.updateSetNum()
                    # update the transition table so any reference of itemSet i becomes itemSet j
                    for k1, v1 in self.transitions.items():
                        for k2, _ in v1.items():
                            if self.transitions[k1][k2] == i:
                                self.transitions[k1][k2] = j
                    break

    def buildActionGoto(self):
        """Build the action and goto tables form the item sets and the transition table."""

        # go through itemSets to get reduction rules
        for itemSetNum, itemSet in self.itemSets.items():
            for item in itemSet:
                if self.seperatorAtEnd(item):
                    for k, v in self.rules.items():
                        if item.lhs == k:
                            for i, r in enumerate(v):
                                if item.rhs == " ".join(r):
                                    if itemSetNum not in self.actions.keys():
                                        self.actions[itemSetNum] = {}
                                    self.actions[itemSetNum][
                                        item.following
                                    ] = "r %s %i" % (k, i)

        # go through transition table to get:
        for k1, v1 in self.transitions.items():
            for k2, v2 in v1.items():
                # goto rules
                if k2 in self.nonTerminals:
                    if k1 not in self.goto.keys():
                        self.goto[k1] = {}
                    self.goto[k1][k2] = v2
                # shift rules
                else:
                    if k1 not in self.actions.keys():
                        self.actions[k1] = {}
                    self.actions[k1][k2] = "s %i" % (v2)

    def loadParseTables(self, grammarFile, force=False):
        """
        Load the saved grammar tables if they exist.
        Otherwise generate new ones and save them.
        """

        grammarName = grammarFile.split("/")[1].split(".")[0]
        tableFile = "{}{}{}".format("tables/", grammarName, "_table.json")

        # Parse the input grammar
        self.parseGrammar(readFile(grammarFile))

        if os.path.isfile(tableFile) and force is False:
            # Load a saved tables file
            print("✔ Reading saved tables...")
            self.loadTables(readFile(tableFile))
        else:
            # Parse the tokens using an LR(1) table
            print("✖ Generating new tables...")
            self.buildTables()
            self.saveTables(tableFile)

    def saveTables(self, tableFileName):
        """Dump the action and goto tables as JSON."""

        with open(tableFileName, "w") as outfile:
            # Save the action table
            json.dump(self.actions, outfile)
            outfile.write("\n")

            # Save the goto table
            json.dump(self.goto, outfile)

    def loadTables(self, tableFile):
        """Parse the saved action and goto tables from the JSON."""

        lines = tableFile.splitlines()
        tempActions = json.loads(lines[0])
        for key, value in tempActions.items():
            self.actions[int(key)] = value
        tempGoto = json.loads(lines[1])
        for key, value in tempGoto.items():
            self.goto[int(key)] = value

    def parse(self, tokens):
        """
        Parse the program (as a list of tokens)
        using our actino and goto tables.
        """

        lookahead = 0
        done = False
        states = [0]
        output = []
        stack = []

        while not done:
            state = states[len(states) - 1]
            realToken = tokens[lookahead]
            if realToken.kind.desc() in self.terminals:
                token = realToken.kind.desc()
            else:
                token = realToken.content

            if debug:
                logging.debug(
                    "---\nState: %s\nStates: %s\nlookahead Token: %s\nstack: %s\noutput: %s\n",
                    state,
                    states,
                    token,
                    stack,
                    output,
                )

            try:
                # Check if we have an entry in our action table for the lookahead token
                if token in self.actions[state].keys():
                    result = self.actions[state][token]
                    output.append(result)
                    result = result.split(" ")

                    # If the action table says to shift, shift the next token
                    if result[0] == "s":
                        states.append(int(result[1]))
                        stack.append(token)
                        lookahead += 1
                        node = grammar.parseToken(token, realToken.content)
                        if node:
                            self.parseTree.append(node)
                        # print("Shifting")

                    # If the action table says to reduce
                    if result[0] == "r":
                        # Get the corresponding rule from our rules table
                        rule = self.rules[result[1]][int(result[2])]

                        # Check if the tokens on the stack match a grammar rule
                        match = True
                        for i, r in enumerate(rule):
                            if r != stack[len(stack) - len(rule) + i]:
                                match = False

                        # If one of the grammar rules matched...
                        if match:
                            # Reduce the tokens on the stack to our new rule token
                            if result[1] != "ACC":
                                tempNode = grammar.parseToken(
                                    result[1],
                                    children=self.parseTree[
                                        len(self.parseTree)
                                        - len(rule) : len(self.parseTree)
                                    ],
                                )
                                del self.parseTree[
                                    len(self.parseTree)
                                    - len(rule) : len(self.parseTree)
                                ]
                                self.parseTree.append(tempNode)
                            del stack[len(stack) - len(rule) : len(stack)]
                            del states[len(states) - len(rule) : len(states)]
                            stack.append(result[1])
                            if debug is True:
                                logging.debug("Reducing rule %s -> %s", result[1], rule)

                            # Check if there is a goto rule for our current state
                            topState = states[-1]
                            topStack = stack[-1]
                            if topStack in self.goto[topState].keys():
                                states.append(self.goto[topState][topStack])
                        else:
                            print(
                                "ERROR: Tried to reduce a rule with invalid tokens on stack."
                            )
                            print("\nExiting Program")
                            return False
                else:
                    print("ERROR: State", state, "Token", token)
                    print(self.actions[state])
                    print("Exiting Program")
                    return False

            except KeyError:
                print(f"ERROR: No entry in the action table for [{state}][{token}]")
                print("Exiting Program")
                return False

            # Check if we have reached the accepting state
            if len(stack) == 1 and stack[0] == "ACC":
                done = True

        if debug:
            logging.debug(output)

        return done

    def updateSetNum(self):
        """Update the number of item sets that we have generated."""

        i = 0
        while self.hasItemSet(i):
            i = i + 1
        self.setNum = i - 1

    def hasItemSet(self, num):
        """Check if the itemSet contains the number."""

        return num in self.itemSets.keys()

    def seperatorAtEnd(self, currItem):
        """Check if there is a separator at the end of the current item."""

        return currItem.seperator >= len(currItem.rhs.split(" "))

    def printRules(self):
        """Output some information about the grammar."""

        print("--- Rules ---")
        for k, v in self.rules.items():
            print(k, ": ", v)
        print("--- NonTerminals ---")
        for nt in self.nonTerminals:
            print(nt)
        print("--- Terminals ---")
        for t in self.terminals:
            print(t)

    def printItemSets(self):
        """Print a list of all the item sets."""

        print("--- Items ---")
        for itemSetNum, itemSet in self.itemSets.items():
            print("Item Set %i: " % (itemSetNum))
            for item in itemSet:
                print("\t", item)

    def printTransitions(self):
        """Print a list of all the transitions."""

        print("--- Transitions ---")
        for k, v in self.transitions.items():
            print(k, v)

    def printTable(self):
        """Print a list of all the action and goto entries."""

        print("--- Actions ---")
        for k, v in self.actions.items():
            print(k, v)
        print("--- Goto ---")
        for k, v in self.goto.items():
            print(k, v)

    def print(self):
        """Print the parse tree."""

        for node in self.parseTree:
            node.print(0)


class Item:
    """
    An item is like a grammar rule.
    There is a LHS of the rule and a RHS.
    A separator that is the dot thing,
    and a following token for the rule.
    """

    def __init__(self, lhs, rhs, seperator, following):
        self.lhs = lhs
        self.rhs = rhs
        self.seperator = seperator
        self.following = following

    def __str__(self):
        rhs = self.rhs.split(" ")
        return "[%s -> %s.%s, %s]" % (
            self.lhs,
            " ".join(rhs[0 : self.seperator]),
            " ".join(rhs[self.seperator : len(self.rhs)]),
            self.following,
        )

    def isSame(self, tempItem):
        """Check if this Item and another Item as the same."""

        return (
            tempItem.lhs == self.lhs
            and tempItem.rhs == self.rhs
            and tempItem.seperator == self.seperator
            and tempItem.following == self.following
        )

    def getRightBefore(self):
        """Return the token directly preceeeding the dot separator."""

        rhs = self.rhs.split(" ")
        if self.seperator - 1 < 0 or self.seperator - 1 >= len(rhs):
            return ""
        return rhs[self.seperator - 1]

    def getRightAfter(self):
        """Return the token directly succeeding the dot separator."""

        rhs = self.rhs.split(" ")
        if self.seperator >= len(rhs):
            return ""
        return rhs[self.seperator]

    def getAfter(self):
        """Return all the tokens after the dot separator."""

        rhs = self.rhs.split(" ")
        return rhs[self.seperator + 1 : len(self.rhs)]

    def incSeperator(self):
        """Make a new Item with the seperator incremented by 1."""

        return Item(self.lhs, self.rhs, self.seperator + 1, self.following)