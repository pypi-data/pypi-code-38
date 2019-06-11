# -*- coding: utf-8 -*-
import re
import logging
from gherkan.containers.StatementTreeNode import StatementTreeNode, StatementTreeOperandNode, StatementTreeBinaryOperatorNode
from lark.tree import Tree
from gherkan.utils import constants as c
from lark import Token
from gherkan.utils import logging_types


class StatementTree():
    def __init__(self, statement : str):
        self.binaryOperators = [c.AND, c.OR]
        self.equalities = [c.EQUALITY, c.INEQUALITY]
        self.statement = statement
        self.root = None

    def buildFromSignalTree(self, tree, negate=False):
        self.root = self.buildSignalNode(tree, parent=None, negate=negate)

    def buildFromNLTree(self, tree):
        self.root = self.buildNLNode(tree)

    def buildSignalNode(self, larkNode, parent=None, negate=False):
        kind = larkNode.data.upper()  # node alias had to be lowercase in the grammar
        str = self.statement[larkNode.meta.start_pos:larkNode.meta.end_pos]
        node = None

        if kind in self.binaryOperators:
            node = StatementTreeBinaryOperatorNode(kind, parent=parent)
            node.lchild = self.buildSignalNode(larkNode.children[0], parent=node, negate=negate)
            node.rchild = self.buildSignalNode(larkNode.children[1], parent=node, negate=negate)

        elif kind in self.equalities:
            node = StatementTreeOperandNode(kind, parent=parent)

            if kind == c.INEQUALITY:
                # there is not "inequality" as a node kind
                node.kind = c.EQUALITY
                negate = True

            node.data.string = str
            node.data.variable = larkNode.children[0].value
            node.data.value = larkNode.children[1].value

        elif kind == c.BOOL:
            node = StatementTreeOperandNode(kind, parent=parent)
            node.data.string = str
            node.data.variable = larkNode.children[0].value
            node.data.value = True

        elif kind == c.NOT:
            # do not save the node, just swap the negate flag and pass it on
            return self.buildSignalNode(larkNode.children[0], parent=parent, negate=not negate)

        elif kind == "FUNCTION":
            # edge, force etc. parsed by lark uniformly as "function"
            function_name = larkNode.children[0].data
            kind = function_name.upper()

            node = StatementTreeOperandNode(kind)
            node.data.string = function_name + str
            node.data.variable = larkNode.children[1].value
            node.data.value = larkNode.children[2].value

        else:
            logging.warning("Unrecognized node: {}", kind, extra={"type": logging_types.W_OPERAND_UNKNOWN, "phrase": str})

        if negate:
            node.negate()

        return node


    def buildNLNode(self, larkNode, parent=None, negate=False):
        if type(larkNode) == Token:
            node = StatementTreeOperandNode(kind=None)
            node.data.variableNL = larkNode.value.strip()
            return node

        kind = larkNode.data.upper()  # node alias had to be lowercase in the grammar
        node = None

        if kind in self.binaryOperators:
            node = StatementTreeBinaryOperatorNode(kind, parent=parent)
            node.lchild = self.buildNLNode(larkNode.children[0], parent=node, negate=negate)
            node.rchild = self.buildNLNode(larkNode.children[1], parent=node, negate=negate)
        elif kind == c.NOT:
            # do not save the node, just swap the negate flag and pass it on
            return self.buildNLNode(larkNode.children[0], parent=parent, negate=not negate)
        else:
            # TODO unrecognized node
            logging.warning("Unrecognized node: {}", kind, extra={"type": logging_types.W_OPERAND_UNKNOWN, "phrase": ""})

        if negate:
            node.negate()

        return node


    # TODO simplify
    def __printNode(self, node: StatementTreeNode, leftChild, levelsOpened):
        string = ''.join([AsciiArt.line + "\t" if lo else "\t" for lo in levelsOpened[:-1]])
        if leftChild:
            if node:
                string += AsciiArt.left + str(str(node) if bool(node) else "ERROR!!!") + '\n'
        else:
            if node:
                string += AsciiArt.right + str(str(node) if bool(node) else "ERROR!!!") + '\n'

        if type(node) is StatementTreeBinaryOperatorNode:
            string += self.__printNode(node.lchild, True, levelsOpened + [True])
            string += self.__printNode(node.rchild, False, levelsOpened + [False])
        return string

    def __str__(self):
        levelsOpened = [False]

        node = self.root
        string = str(node) + '\n'
        if type(node) is StatementTreeBinaryOperatorNode:
            string += self.__printNode(node.lchild, True, levelsOpened + [True])
            string += self.__printNode(node.rchild, False, levelsOpened + [False])
        return string


class AsciiArt:
    dash = '\u2500'
    line = '\u2502'
    left = '\u251c\u2500\u2500 '
    right = '\u2514\u2500\u2500 '

