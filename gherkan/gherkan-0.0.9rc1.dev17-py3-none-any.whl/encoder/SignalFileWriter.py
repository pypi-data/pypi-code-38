# -*- coding: utf-8 -*-
from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.containers.signal_batch import SignalBatch
from gherkan.containers.StatementTreeNode import StatementTreeBinaryOperatorNode, \
    StatementTreeNode, StatementTreeOperandNode, StatementTreeMergedNode
from gherkan.containers.StatementTree import StatementTree
from gherkan.processing.TreeProcessor import TreeProcessor

import gherkan.utils.constants as c
import gherkan.utils.gherkin_keywords as g
from gherkan.utils import logging_types

import logging

class SignalFileWriter():
    """ TODO docs """

    def __init__(self, nmm : NLPModelManager):
        self.nlBatch = None
        self.outLines = []
        self.language = None
        self.nmm = nmm
        self.feature = ""

    def encode(self, nlBatch: SignalBatch, no_processing: bool = False):
        self.nlBatch = nlBatch
        self.language = nlBatch.language
        self.no_processing = no_processing
        self.feature = nlBatch.name

        self.outLines.append("# language: {}\n\n".format(self.language))
        self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Feature"), nlBatch.name))
        self.outLines.append("  {}\n".format(nlBatch.desc))

        if nlBatch.context:
            self.outLines.append("{}:\n".format(g.get_kw(self.language, "Background")))
            self.outLines.append("  {} {}\n\n".format(g.get_kw(self.language, "Given"), self.tree_to_str(nlBatch.context)))

        for scenario in nlBatch.scenarios:
            self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Scenario"), scenario.name))

            for tree in scenario.givenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "Given"), self.tree_to_str(tree)))
            for tree in scenario.whenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "When"), self.tree_to_str(tree)))
            for tree in scenario.thenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "Then"), self.tree_to_str(tree)))


    def write(self, outputFilePath: str):
        with open(outputFilePath, "w", encoding="utf-8") as out:
            out.writelines(self.outLines)

    def tree_to_str(self, tree: StatementTree):
        if not self.no_processing:
            tp = TreeProcessor(self.language, self.nmm, self.feature)

            # loads yaml file with templates
            tp.load_templ_dic('utils/templates_dic.yaml')
            tree.root = tp.process_tree(tree.root, TreeProcessor.Direction.NL_TO_SIGNAL)

        return self.node_to_str(tree.root)

    def node_to_str(self, node: StatementTreeNode):
        if type(node) == StatementTreeBinaryOperatorNode:
            return self.operator_to_str(node)
        elif type(node) == StatementTreeMergedNode:
            return self.merged_operator_to_str(node)
        elif type(node) == StatementTreeOperandNode:
            return self.operand_to_str(node)

    def merged_operator_to_str(self, node: StatementTreeMergedNode):
        return " && ".join([self.operand_to_str(subnode) for subnode in node.subnodes])

    def operator_to_str(self, node: StatementTreeBinaryOperatorNode):
        if node.kind == c.AND:
            operator = "&&"
        elif node.kind == c.OR:
            operator = "||"
        else:
            raise NotImplementedError("Unrecognized operator {}".format(node.kind))

        return ("({}) {} ({})".format(
            self.node_to_str(node.lchild),
            operator,
            self.node_to_str(node.rchild)))

    def operand_to_str(self, node: StatementTreeOperandNode):
        kind = node.kind

        if kind == c.EQUALITY:
            return "{} {}= {}".format(
                node.data.variable,
                "!" if node.negated else "=",
                node.data.value
            )
        elif kind == c.BOOL:
            return "{}{}".format(
                # XOR in case boolean is negated by the 'negated' attribute
                "" if (node.data.value ^ node.negated) else "! ",
                node.data.variable,
            )
        elif kind in [c.EDGE,
                      c.FORCE,
                      c.UNFORCE]:
            return "{}{}({}, {})".format(
                "! " if node.negated else "",
                node.kind.lower(),
                node.data.variable,
                node.data.value
            )
        else:
            logging.warning("Node kind {} not recognized!", kind, extra={"type": logging_types.W_OPERAND_UNKNOWN, "phrase": ""})
