# -*- coding: utf-8 -*-
from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.containers.signal_batch import SignalBatch
from gherkan.containers.StatementTreeNode import StatementTreeBinaryOperatorNode, \
    StatementTreeNode, StatementTreeOperandNode, StatementTreeMergedNode
from gherkan.containers.StatementTree import StatementTree
from gherkan.processing.TreeProcessor import TreeProcessor
import gherkan.utils.gherkin_keywords as g
import gherkan.utils.constants as c


class NLFileWriter():
    """ TODO docs """

    def __init__(self, nmm : NLPModelManager):
        self.signalBatch = None
        self.outLines = []
        self.language = None
        self.nmm = nmm
        self.feature = ""

    def encode(self, signalBatch: SignalBatch):
        self.signalBatch = signalBatch
        self.language = signalBatch.language
        self.feature = signalBatch.name

        self.outLines.append("# language: {}\n\n".format(self.language))
        self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Feature"), signalBatch.name))
        self.outLines.append("  {}\n".format(signalBatch.desc))

        if signalBatch.context:
            self.outLines.append("{}:\n".format(g.get_kw(self.language, "Background")))
            self.outLines.append("  {} {}\n\n".format(
                g.get_kw(self.language, "Given"), self.tree_to_str(signalBatch.context)))

        for scenario in signalBatch.scenarios:
            self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Scenario"), scenario.name))

            for tree in scenario.givenStatements:
                self.outLines.append("  {} {}\n".format(
                    g.get_kw(self.language, "Given"), self.tree_to_str(tree)))
            for tree in scenario.whenStatements:
                self.outLines.append("  {} {}\n".format(
                    g.get_kw(self.language, "When"), self.tree_to_str(tree)))
            for tree in scenario.thenStatements:
                self.outLines.append("  {} {}\n".format(
                    g.get_kw(self.language, "Then"), self.tree_to_str(tree)))

    def write(self, outputFilePath: str):
        with open(outputFilePath, "w", encoding="utf-8") as out:
            out.writelines(self.outLines)

    def tree_to_str(self, tree: StatementTree):
        tp = TreeProcessor(self.language, self.nmm, self.feature)

        # loads yaml file with templates
        tp.load_templ_dic('utils/templates_dic.yaml')
        tree.root = tp.process_tree(
            tree.root, TreeProcessor.Direction.SIGNAL_TO_NL)

        return self.node_to_str(tree.root)

    def node_to_str(self, node: StatementTreeNode):
        if type(node) == StatementTreeBinaryOperatorNode:
            return self.operator_to_str(node)
        elif type(node) == StatementTreeOperandNode or \
                type(node) == StatementTreeMergedNode:
            return self.operand_to_str(node)

    def operator_to_str(self, node: StatementTreeBinaryOperatorNode):
        return ("({} {} {})".format(
            self.node_to_str(node.lchild),
            node.kind.upper(),
            self.node_to_str(node.rchild))
        )

    def operand_to_str(self, node: StatementTreeOperandNode):
        return "{}".format(node.data.variableNL)
