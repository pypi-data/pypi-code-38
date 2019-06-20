# -*- coding: utf-8 -*-
from gherkan.utils import constants as c


class StatementTreeNode():
    def __init__(self, kind, parent):
        self.kind = kind
        self.parent = parent
        self.negated = False


    def negate(self):
        self.negated = not self.negated


    def isNegated(self):
        return self.negated


class StatementTreeBinaryOperatorNode(StatementTreeNode):
    def __init__(self, kind, parent=None):
        super().__init__(kind, parent)
        self.lchild = None
        self.rchild = None

    def __str__(self):
        return 'Operator(type: {})'.format(self.kind)

    def negate(self):
        if self.kind == c.AND:
            self.kind = c.OR
        elif self.kind == c.OR:
            self.kind = c.AND
        else:
            raise NotImplementedError("Cannot negate {}".format(self.kind))


class StatementTreeOperandNode(StatementTreeNode):
    def __init__(self, kind, parent=None):
        super().__init__(kind, parent)
        self.data = StatementTreeNodeData()

    def __str__(self):
        return 'Operand(type: {}, variable: {}, value: {}, variableNLP: {})'.format(
            self.kind, self.data.variable, self.data.value, self.data.variableNL)


class StatementTreeMergedNode(StatementTreeNode):
    def __init__(self, kind="MERGED_NODE", parent=None):
        super().__init__(kind, parent)
        self.subnodes = []
        self.data = StatementTreeNodeData()

    def __str__(self):
        return 'MergedNode(contains {} nodes)'.format(len(self.subnodes))

class StatementTreeNodeData():
    def __init__(self):
        self.string = None
        self.variable = None
        self.value = None
        self.variableNL = None
        self.valueId = None