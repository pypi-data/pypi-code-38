# -*- coding: utf-8 -*-
# Python version: 2/3
#
# AST Tree class
# Simon Fraser University
# Jetic Gu
#
# This module contains functions and classes necessary for loading single lined
# penn treebank format AST Trees.
#
from __future__ import absolute_import
import sys
import os
import unittest
import inspect
from copy import deepcopy

from natlang.format.tree import Node as BaseNode


class AstNode(BaseNode):
    '''
    This is the main data structure of a tree, an AstNode instance is a node on
    the tree. The structure of the subtree with node x as root can be viewed by
    calling x.__repr__()
    '''
    def __init__(self, parent=None):
        BaseNode.__init__(self, parent)
        return

    def __repr__(self):
        return 'AstNode({})'.format(repr(self.value))

    def export(self):
        '''
        One should always implement their own exporter though
        '''
        return BaseNode.export(self)


def constructTreeFromStr(string, rootLabel="ROOT"):
    '''
    This method constructs a tree from a string.
    @param string: str, in Penn Treebank format
    @return root: AstNode, the root node.
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
    @return root: AstNode, the root node.
    '''
    root = None
    currentParent = None
    current = None
    for element in elements:
        if element == "(":
            currentParent = current
            current = AstNode(parent=currentParent)
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
                root = AstNode()
                root.value = ("NaN", "NaN")
                return root
            if openClauses == 1:
                openClauses = 0
                tmp = AstNode(current)
                current.child = tmp
            else:
                tmp = AstNode(current.parent)
                current.sibling = tmp
            tmp.value = ('NaN', action[1])
            current = tmp
        elif action[0] == "NT":
            if root is None:
                tmp = AstNode()
                root = tmp
            elif openClauses == 1:
                tmp = AstNode(current)
                current.child = tmp
            else:
                tmp = AstNode(current.parent)
                current.sibling = tmp
            tmp.value = (action[1],)
            current = tmp
            openClauses = 1
        else:
            if root is None:
                root = AstNode()
                root.value = ("NaN", "NaN")
                return root
            current = current.parent

    root.calcId(1)
    root.calcPhrase(force=True)
    return root


def createSketch(node, sketchLabels, phGenerator):
    # Let's say all values are considered here.
    if not isinstance(node, AstNode):
        raise ValueError("Incorrect argument type: has to be an AstNode")
    result = deepcopy(node)

    def _lexicaliseUsingSketchLabels(node):
        if node.child is None:
            v1, v2 = node.value
            if v1 not in sketchLabels:
                node.value = (phGenerator(v1), v2)
            if v2 not in sketchLabels:
                node.value = (v1, phGenerator(v2))
        else:
            v1, = node.value
            if v1 not in sketchLabels:
                node.value = (phGenerator(v1), )
            _lexicaliseUsingSketchLabels(node.child)
        if node.sibling is not None:
            _lexicaliseUsingSketchLabels(node.sibling)
        return

    _lexicaliseUsingSketchLabels(result)
    result.calcPhrase(force=True)
    return


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
        # print x.__repr__()
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
        # print x.__repr__()
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
        # print y.__repr__()
        self.assertSequenceEqual(y.phrase, [('NP', 3), ('VP', 1), ('NP', 2)])

        int2w = {0: '<UNK>', 1: 'likes', 2: 'cheese', 3: 'Andrei'}
        z = lexicaliseNode(y, int2w)
        # print y.__repr__()
        self.assertSequenceEqual(
            z.phrase, [('NP', "Andrei"), ('VP', "likes"), ('NP', "cheese")])
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
        # print x.__repr__()
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
