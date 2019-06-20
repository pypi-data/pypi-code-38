# -*- coding: utf-8 -*-
"""
"""
from gherkan.containers.StatementTreeNode import StatementTreeBinaryOperatorNode, \
    StatementTreeNode, StatementTreeOperandNode, StatementTreeMergedNode
from gherkan.containers.StatementTree import StatementTree
from gherkan.decoder.SignalParser import SignalParser

import gherkan.utils.constants as c
import gherkan.utils.gherkin_keywords as g
from gherkan.utils import logging_types
import os
import json

import logging


class SignalMapper():

    def __init__(self, dictFilePath: str):
        self.batch = None
        self.language = None
        self.feature = ""
        self.dictionary = {}
        self.dictFilePath = dictFilePath
        if os.path.exists(dictFilePath):  # check if a dictionary exists
            self._loadDictionary()  # load the dict
        else:
            self._writeDictionary()  # if it does not exist, write an empty one

    def loadSignal(self, signalFilePath: str):
        sp = SignalParser()
        self.outLines = []
        self.batch = sp.parseFile(signalFilePath)
        self.language = self.batch.language
        self.feature = self.batch.name

    # <=== Analysis ===>
    def _appendToDict(self, item):
        if item not in self.dictionary:
            self.dictionary[item] = item

    def analyze(self):
        if self.batch is None:
            Exception("Signal file was not loaded, yet!")
        batch = self.batch

        if batch.context:
            self._analyze_node(batch.context.root)

        for scenario in batch.scenarios:
            for tree in scenario.givenStatements:
                self._analyze_node(tree.root)
            for tree in scenario.whenStatements:
                self._analyze_node(tree.root)
            for tree in scenario.thenStatements:
                self._analyze_node(tree.root)

    def _analyze_node(self, node: StatementTreeNode):
        if isinstance(node, StatementTreeBinaryOperatorNode):
            self._analyze_operator(node)
        elif isinstance(node, StatementTreeMergedNode):
            self._analyze_merged_operator(node)
        elif isinstance(node, StatementTreeOperandNode):
            self._analyze_operand(node)

    def _analyze_merged_operator(self, node: StatementTreeMergedNode):
        for subnode in node.subnodes:
            self._analyze_operand(subnode)

    def _analyze_operator(self, node: StatementTreeBinaryOperatorNode):
        if not (node.kind == c.AND or node.kind == c.OR):
            raise NotImplementedError("Unrecognized operator {}".format(node.kind))
        self._analyze_node(node.lchild)
        self._analyze_node(node.rchild)

    def _analyze_operand(self, node: StatementTreeOperandNode):
        signal = node.data.variable
        self._appendToDict(signal)

    def writeDictionary(self):
        with open(self.dictFilePath, "w", encoding="utf-8") as dictFile:
            json.dump(self.dictionary, dictFile, ensure_ascii=False, indent=4)

    def _loadDictionary(self):
        with open(self.dictFilePath, "r", encoding="utf-8") as dictFile:
            self.dictionary = json.load(dictFile)

    # <=== Signal Writing ===>
    def encode(self):
        if self.batch is None:
            Exception("Signal file was not loaded, yet!")
        batch = self.batch

        self.outLines.append("# language: {}\n\n".format(self.language))
        self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Feature"), batch.name))
        self.outLines.append("  {}\n".format(batch.desc))

        if batch.context:
            self.outLines.append("{}:\n".format(g.get_kw(self.language, "Background")))
            self.outLines.append("  {} {}\n\n".format(g.get_kw(self.language, "Given"), self.tree_to_str(batch.context)))

        for scenario in batch.scenarios:
            self.outLines.append("{}: {}\n".format(g.get_kw(self.language, "Scenario"), scenario.name))

            for tree in scenario.givenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "Given"), self.tree_to_str(tree)))
            for tree in scenario.whenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "When"), self.tree_to_str(tree)))
            for tree in scenario.thenStatements:
                self.outLines.append("  {} {}\n".format(g.get_kw(self.language, "Then"), self.tree_to_str(tree)))

    def writeSignal(self, outputFilePath: str):
        with open(outputFilePath, "w", encoding="utf-8") as out:
            out.writelines(self.outLines)

    def tree_to_str(self, tree: StatementTree):
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
        variable = node.data.variable
        if variable in self.dictionary:
            variable = self.dictionary[variable]
        else:
            logging.warning("Signal name not found in the mapping dictionary: {}; keeping the original name.", variable, extra={"type": logging_types.W_MAPPING_NOT_DEFINED, "phrase": str(node)})

        outString = ""
        if kind == c.EQUALITY:
            outString = "{} {}= {}".format(
                variable,
                "!" if node.negated else "=",
                node.data.value
            )
        elif kind == c.BOOL:
            outString = "{}{}".format(
                # XOR in case boolean is negated by the 'negated' attribute
                "" if (node.data.value ^ node.negated) else "! ",
                variable,
            )
        elif kind in [c.EDGE,
                      c.FORCE,
                      c.UNFORCE]:
            outString = "{}{}({}, {})".format(
                "! " if node.negated else "",
                node.kind.lower(),
                variable,
                node.data.value
            )
        else:
            logging.warning("Node kind {} not recognized!", kind, extra={"type": logging_types.W_OPERAND_UNKNOWN, "phrase": str(node)})

        return outString

    def __del__(self):
        # self.writeDictionary()
        pass


# signalFileMapper = SignalMapper()
# signalFileMapper.loadSignal(r"C:\Users\admin\Documents\nl_instruction_processing\data\input\Scenare\Montrac_signals.feature")
# # signalFileMapper.analyze()

# # signalFileMapper.dictionary["robotR3ProgamEnd"] = "programEnd"
# signalFileMapper.loadDictionary(r"C:\Users\admin\Documents\test.json")
# signalFileMapper.encode()
