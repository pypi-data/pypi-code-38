# -*- coding: utf-8 -*-
# Python version: 2/3
#
# Constituency Tree class
# Simon Fraser University
# Jetic Gu
#
# This module contains functions and classes necessary for loading single lined
# penn treebank format sentences with constituency information. 2 examples are
# provided in TestTree.
#
from __future__ import absolute_import
import sys
import os
import unittest
import inspect
from copy import deepcopy


class Node:
    '''
    This is the main data structure of a tree, a Node instance is a node on the
    tree. The structure of the subtree with node x as root can be viewed by
    calling x.onScreen()
    '''
    def __init__(self, parent=None):
        self.value = ()
        self.phrase = []
        self.id = 0
        self.parent = parent
        self.sibling = None
        self.child = None
        self.depth = -1
        return

    def onScreen(self, __spacing="", __showSibling=False):
        '''
        This method prints the structure of the subtree with self as root.
        '''
        if self.child is not None:
            print(__spacing + str((self.id,) + self.value)[:-1])
            self.child.onScreen(__spacing + "  ", True)
            print(__spacing + ")")
        else:
            print(__spacing + str((self.id,) + self.value))
        if self.sibling is not None and __showSibling is True:
            self.sibling.onScreen(__spacing, True)
        return

    def __iter__(self):
        return iter([w for t, w in self.phrase])

    def __len__(self):
        return len(self.phrase)

    def export(self):
        result = "("
        if self.child is None:
            result += str(self.value[0]) + " " + str(self.value[1]) + ")"
        else:
            result += str(self.value[0]) + " " + self.child.export() + ")"
        if self.sibling is not None:
            result += " " + self.sibling.export()
        return result

    def refresh(self):
        '''
        This method recalculates the ID and repropagates self.phrase
        '''
        tmp = self
        while (tmp.parent is not None):
            tmp = tmp.parent
        tmp.calcId(1)
        self.calcPhrase(force=True)
        return

    def calcId(self, id):
        '''
        This method calculates the ids of all nodes in the subtree using
        breadth-first search.
        @param id: id of self, also the starting point
        '''
        self.id = id
        queue = [self]
        while len(queue) != 0:
            newQueue = []
            for node in queue:
                tmp = node.child
                if tmp is None and len(node.value) != 2:
                    node.value += node.value
                    if len(node.value) != 2:
                        raise RuntimeError
                if tmp is not None and len(node.value) != 1:
                    raise RuntimeError
                if tmp is not None and "-" in node.value[0]:
                    newClauseType = node.value[0].split("-")[0]
                    node.value = (newClauseType,)
                while tmp is not None:
                    newQueue.append(tmp)
                    tmp.id = id + 1
                    id += 1
                    tmp = tmp.sibling
            queue = newQueue
        return

    def calcPhrase(self, force=False):
        if self.phrase == [] or self.depth <= 0 or force is True:
            self.phrase = []
            self.depth = 1
            if self.child is not None:
                self.child.calcPhrase(force)
                self.depth = max(self.depth, self.child.depth + 1)
            if self.sibling is not None:
                self.sibling.calcPhrase(force)
                self.depth = max(self.depth, self.sibling.depth)
        if self.child is None:
            self.phrase = [self.value]
        else:
            tmp = self.child
            while tmp is not None:
                self.phrase += tmp.phrase
                tmp = tmp.sibling
        return

    def columnFormat(self, parColumn=None, sibColumn=None,
                     valColumn=None, hasChild=None, hasSibl=None, LM=False):
        '''
        This method returns the fraternal info and ancestral info columns.
        @return anc, fra: lists
            anc[i] is the id of ancester of node i,
            fra[i] is the id of previous sibling of node i,
            val[i] is the label of node i,
        '''
        if parColumn is None or sibColumn is None or valColumn is None or\
                hasChild is None or hasSibl is None:
            parColumn = []
            sibColumn = []
            valColumn = []
            hasChild = []
            hasSibl = []
        while len(parColumn) <= self.id:
            parColumn.append(0)
            sibColumn.append(0)
            hasChild.append(0)
            hasSibl.append(0)
            valColumn.append(("NULL",))
        valColumn[self.id] = self.value

        if self.parent is not None:
            parColumn[self.id] = self.parent.id
            if self.parent.child != self:
                sibColumn[self.id] = self.id - 1
            else:
                if LM is True:
                    sibColumn[self.id] = sibColumn[self.parent.id]

        if self.child is not None:
            hasChild[self.id] = 1
            self.child.columnFormat(
                parColumn, sibColumn, valColumn, hasChild, hasSibl, LM)
        if self.sibling is not None:
            hasSibl[self.id] = 1
            self.sibling.columnFormat(
                parColumn, sibColumn, valColumn, hasChild, hasSibl, LM)
        return parColumn, sibColumn, valColumn, hasChild, hasSibl

    def columnFormatWordIndex(self, column=None, start=0):
        if column is None:
            column = []
        while len(column) <= self.id:
            column.append(0)
        column[self.id] = start
        if self.child is not None:
            self.child.columnFormatWordIndex(column, start=start)
        if self.sibling is not None:
            self.sibling.columnFormatWordIndex(column, start=start + len(self))
        return column


def constructTreeFromStr(string, rootLabel="ROOT"):
    '''
    This method constructs a tree from a string.
    @param string: str, in Penn Treebank format
    @return root: Node, the root node.
    '''
    if string.strip() == "(())":
        return None
    newString = string.replace("(", " ( ").replace(")", " ) ")
    try:
        return constructTree(newString.split(), rootLabel)
    except AttributeError as e:
        return None


def constructTree(elements, rootLabel="ROOT"):
    '''
    This method constructs a tree from a list of elements. Each bracket is
    considered an independent element.
    @param elements: list of str, in Penn Treebank format
    @return root: Node, the root node.
    '''
    root = None
    currentParent = None
    current = None
    for element in elements:
        if element == "(":
            currentParent = current
            current = Node(parent=currentParent)
            if currentParent is not None:
                if currentParent.child is not None:
                    tmp = currentParent.child
                    while tmp.sibling is not None:
                        tmp = tmp.sibling
                    tmp.sibling = current
                else:
                    currentParent.child = current
            else:
                root = current

        elif element == ")":
            current = current.parent
            if current is not None:
                currentParent = current.parent
        else:
            current.value += (element,)
    if root is not None:
        if root.value == ():
            root.value = (rootLabel,)
        try:
            root.refresh()
        except RuntimeError:
            return None
    return root


def constructTreeFromRNNGAction(actions):
    root = None
    current = root
    openClauses = 0
    for action in actions:
        if action[0] == "GEN":
            if root is None:
                root = Node()
                root.value = ("NaN", "NaN")
                return root
            if openClauses == 1:
                openClauses = 0
                tmp = Node(current)
                current.child = tmp
            else:
                tmp = Node(current.parent)
                current.sibling = tmp
            tmp.value = ('NaN', action[1])
            current = tmp
        elif action[0] == "NT":
            if root is None:
                tmp = Node()
                root = tmp
            elif openClauses == 1:
                tmp = Node(current)
                current.child = tmp
            else:
                tmp = Node(current.parent)
                current.sibling = tmp
            tmp.value = (action[1],)
            current = tmp
            openClauses = 1
        else:
            if root is None:
                root = Node()
                root.value = ("NaN", "NaN")
                return root
            current = current.parent

    root.refresh()
    return root


def load(fileName, linesToLoad=sys.maxsize, verbose=True):
    import progressbar
    fileName = os.path.expanduser(fileName)
    content = []
    i = 0
    widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(),
               progressbar.FormatLabel(
               '; Total: %(value)d sents (in: %(elapsed)s)')]
    with open(fileName) as file:
        if verbose is True:
            loadProgressBar =\
                progressbar.ProgressBar(widgets=widgets,
                                        maxval=min(
                                            sum(1 for line in file),
                                            linesToLoad)).start()
            file.seek(0)
        for line in file:
            i += 1
            if verbose is True:
                loadProgressBar.update(i)
            content.append(constructTreeFromStr(line))
            if i == linesToLoad:
                break

    if verbose is True:
        loadProgressBar.finish()
    return content


def lexicaliseNode(root, wLex, tLex=None, lLex=None):
    '''
    @param wLex: dist, word lexicon
    @param tLex: dist, postag lexicon
    @param lLex: dist, label lexicon
    '''
    def value2int(node):
        if node.child is None:
            if node.value[1] in wLex:
                node.value = (node.value[0], wLex[node.value[1]])
            else:
                node.value = (node.value[0], wLex["<UNK>"])
            if tLex is not None:
                if node.value[0] in tLex:
                    node.value = (tLex[node.value[0]], node.value[1])
                else:
                    node.value = (tLex["<UNK>"], node.value[1])
        else:
            if lLex is not None:
                if node.value[0] in lLex:
                    node.value = (lLex[node.value[0]],)
                else:
                    node.value = (lLex["<UNK>"],)
        return node

    newRoot = deepcopy(root)
    value2int(newRoot)
    queue = [newRoot]
    while len(queue) != 0:
        newQueue = []
        for node in queue:
            tmp = node.child
            while tmp is not None:
                newQueue.append(tmp)
                value2int(tmp)
                tmp = tmp.sibling
        queue = newQueue
    newRoot.calcPhrase(force=True)
    return newRoot


def constructRNNGAction(root):
    result = []
    if root.child is None:
        result += [("GEN", root.value[1])]
    else:
        result += [("NT", root.value[0])]
        result += constructRNNGAction(root.child)
        result += [("REDUCE",)]
    if root.sibling is not None:
        result += constructRNNGAction(root.sibling)
    return result


class TestTree(unittest.TestCase):
    def testBuildTreeA(self, x=None):
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        if x is None:
            x = constructTree(elements)
        # print x.onScreen()
        anc, fra, val, child, sibl = x.columnFormat()
        ancG = [0, 0, 1, 2, 2, 4, 4]
        fraG = [0, 0, 0, 0, 3, 0, 5]
        valG = [('NULL',), ('ROOT',), ('S',), ('NP', 'Andrei'), ('VP',),
                ('VP', 'likes'), ('NP', 'cheese')]
        self.assertSequenceEqual(anc, ancG)
        self.assertSequenceEqual(fra, fraG)
        self.assertSequenceEqual(val, valG)
        return

    def testBuildTreeB(self, x=None):
        elements = "( ROOT ( FRAG ( NP ( NNP Madam ) ( NNP President ) )" +\
            " ( , , ) ( PP ( IN on ) ( NP ( NP ( DT a ) ( NN point ) ) (" +\
            " PP ( IN of ) ( NP ( NN order ) ) ) ) ) ( . . ) ) )"
        if x is None:
            x = constructTreeFromStr(elements)
        # print x.onScreen()
        anc, fra, val, child, sibl = x.columnFormat()
        ancG = [0, 0, 1, 2, 2, 2, 2, 3, 3, 5, 5, 10, 10, 11, 11, 12, 12, 16]
        fraG = [0, 0, 0, 0, 3, 4, 5, 0, 7, 0, 9, 0, 11, 0, 13, 0, 15, 0]
        valG = [('NULL',), ('ROOT',), ('FRAG',), ('NP',), (',', ','), ('PP',),
                ('.', '.'), ('NNP', 'Madam'), ('NNP', 'President'),
                ('IN', 'on'), ('NP',), ('NP',), ('PP',), ('DT', 'a'),
                ('NN', 'point'), ('IN', 'of'), ('NP',), ('NN', 'order')]
        self.assertSequenceEqual(anc, ancG)
        self.assertSequenceEqual(fra, fraG)
        self.assertSequenceEqual(val, valG)
        return

    def testLoadTreeFromFile(self):
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        content = load(parentdir + "/test/sampleTree.txt", verbose=False)
        A = content[0]
        B = content[1]
        self.testBuildTreeA(A)
        self.testBuildTreeB(B)
        return

    def testLoadTreeFromLoader(self):
        from natlang.loader import DataLoader
        currentdir = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir)
        loader = DataLoader("tree")
        content = loader.load(parentdir + "/test/sampleTree.*", verbose=False)
        A = content[0]
        B = content[1]
        self.testBuildTreeA(A)
        self.testBuildTreeB(B)
        return

    def testLexicaliseNode(self):
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        x = constructTree(elements)
        w2int = {'<UNK>': 0, 'likes': 1, 'cheese': 2, 'Andrei': 3}
        y = lexicaliseNode(x, w2int)
        # print y.onScreen()
        self.assertSequenceEqual(y.phrase, [('NP', 3), ('VP', 1), ('NP', 2)])

        int2w = {0: '<UNK>', 1: 'likes', 2: 'cheese', 3: 'Andrei'}
        z = lexicaliseNode(y, int2w)
        # print y.onScreen()
        self.assertSequenceEqual(
            z.phrase, [('NP', "Andrei"), ('VP', "likes"), ('NP', "cheese")])
        return

    def testExportNode(self):
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        x = constructTree(elements)
        self.assertEqual(elements, x.export().replace(
            "(", " ( ").replace(")", " ) ").split())
        return

    def testBuildTreeLM(self, x=None):
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        if x is None:
            x = constructTree(elements)
        # print x.onScreen()
        anc, fra, val, child, sibl = x.columnFormat(LM=True)
        ancG = [0, 0, 1, 2, 2, 4, 4]
        fraG = [0, 0, 0, 0, 3, 3, 5]
        valG = [('NULL',), ('ROOT',), ('S',), ('NP', 'Andrei'), ('VP',),
                ('VP', 'likes'), ('NP', 'cheese')]
        self.assertSequenceEqual(anc, ancG)
        self.assertSequenceEqual(fra, fraG)
        self.assertSequenceEqual(val, valG)
        return

    def testColumnFormatWordIndex(self, x=None):
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        if x is None:
            x = constructTree(elements)
        realColumn = [0, 0, 0, 0, 1, 1, 2]
        self.assertSequenceEqual(realColumn, x.columnFormatWordIndex())


if __name__ == '__main__':
    if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        unittest.main()
    else:
        elements = ["(", "ROOT",
                    "(", "S",
                    "(", "NP", "Andrei", ")",
                    "(", "VP", "(", "VP", "likes", ")",
                    "(", "NP", "cheese", ")",
                    ")",
                    ")",
                    ")"]
        x = constructTree(elements)
        elements = "( ROOT ( FRAG ( NP ( NNP Madam ) ( NNP President ) )" +\
            " ( , , ) ( PP ( IN on ) ( NP ( NP ( DT a ) ( NN point ) ) (" +\
            " PP ( IN of ) ( NP ( NN order ) ) ) ) ) ( . . ) ) )"
        y = constructTreeFromStr(elements)
        print("Use the two Nodes x and y for testing new methods on Node.")
        print("Use unittest.main() to start unit test")
