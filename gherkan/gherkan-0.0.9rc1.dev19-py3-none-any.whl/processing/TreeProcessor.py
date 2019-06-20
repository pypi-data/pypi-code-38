# -*- coding: utf-8 -*-
import re

import pkg_resources
import yaml
import logging

from gherkan.containers.NLPModelManager import NLPModelManager
from gherkan.utils import logging_types

from gherkan.containers.SignalPhrase import SignalPhrase
from gherkan.containers.StatementTreeNode import StatementTreeBinaryOperatorNode, StatementTreeOperandNode, \
    StatementTreeNode, StatementTreeMergedNode

from gherkan.encoder.NL2Temp import NLTempMatcher

from enum import Enum
from pprint import pprint as pp
from gherkan.processing.Temp2NL import FillActions
from gherkan.utils import constants as c


class TreeProcessor:
    class Direction(Enum):
        SIGNAL_TO_NL = 0
        NL_TO_SIGNAL = 1

    def __init__(self, language : str, nmm : NLPModelManager, feature: str):
        self.templ_dic = None
        self.language = language
        self.nmm = nmm

        self.ntm = NLTempMatcher(lang=self.language, nmm=self.nmm, feature=feature)


    def process_tree(self, node: StatementTreeNode, dir: Direction):
        if dir not in [TreeProcessor.Direction.SIGNAL_TO_NL,
                       TreeProcessor.Direction.NL_TO_SIGNAL]:

            err_msg = "Direction {} unknown".format(dir)
            logging.error(err_msg)

        self.dir = dir


        return self.process_tree_recursive(node)


    def process_tree_recursive(self, node: StatementTreeNode):
        if type(node) is StatementTreeBinaryOperatorNode:

            if self.dir == TreeProcessor.Direction.SIGNAL_TO_NL and node.kind == c.AND:
                # try to match compound template which can be rooted in the AND node
                res = self.match_compound_signal_templates(node)

                # in case the compound template has been matched, replace the AND node
                # at the parent by the new merged node
                if res:
                    template, matches, merged_node = res
                    self.process_operand(merged_node, matches, template)
                    return merged_node

            node.lchild = self.process_tree_recursive(node.lchild)
            node.rchild = self.process_tree_recursive(node.rchild)

        elif type(node) is StatementTreeOperandNode:

            if self.dir == TreeProcessor.Direction.NL_TO_SIGNAL:
                # normalize NL phrase before template matching
                res = self.ntm.get_NLPhrase(node.data.variableNL)
                node.data.variableNL = res["tempToNL"]

                self.add_node_modifiers(node, res)

                match, template = self.match_simple_templates(node)

                if match is None:
                    logging.warning("No match found for phrase '{}'.", node.data.variableNL,
                                    extra={"type": logging_types.W_TEMPLATE_NOT_FOUND, "phrase": node.data.variableNL})
                    return

                node = self.process_operand(node, [match], template)

            elif self.dir == TreeProcessor.Direction.SIGNAL_TO_NL:
                match, template = self.match_simple_templates(node)

                if match is None:
                    logging.warning("No match found for phrase '{}'.", node.data.variableNL,
                                    extra={"type": logging_types.W_TEMPLATE_NOT_FOUND, "phrase": node.data.string})
                    return

                node = self.process_operand(node, [match], template)

        else:
            err_msg = "Unrecognized type of node: {}".format(type(node))
            logging.error(err_msg)

        # returned node should be reassigned in case the node changed
        return node



    def add_node_modifiers(self, node, res):
        if res["state"] is not None:
            # TODO this is only a temporary solution: state is appended at the end of the phrase and matched with a template
            # TODO should be handled by NLTempMatcher
            node.data.variableNL += ":" + res["state"]

        if res["value"] is not None:
            node.data.value = res["value"]

        if res["negate"]:
            node.negate()
        elif res["force"]:
            node.kind = c.FORCE
        elif "edge" in res and res["edge"]:  # TODO remove ("edge" in res) -> should be there always
            node.kind = c.EDGE


    def process_operand(self, node: StatementTreeNode, matches: list, template):
        sp = SignalPhrase()
        sp.tempName = template["Name"]
        sp.tempStr = template["SignalTemplate"]
        sp.tempToNL = template["NLTemplateEn"] if self.language == c.LANG_EN else template["NLTemplateCz"]
        sp.inclinations = template["Inclinations"]
        sp.language = self.language
        sp.negate = node.isNegated()
        sp.force = (node.kind == c.FORCE)
        sp.edge = (node.kind == c.EDGE)

        for match in matches:
            for key, val in match.groupdict().items():
                sp.vars[key] = val

        if self.dir == TreeProcessor.Direction.SIGNAL_TO_NL:
            if type(node) == StatementTreeOperandNode:
                sp.values[node.data.valueId] = node.data.value

            elif type(node) == StatementTreeMergedNode:
                for subnode in node.subnodes:
                    sp.values[subnode.data.valueId] = subnode.data.value

            self.translate_to_nl(node, sp)
        elif self.dir == TreeProcessor.Direction.NL_TO_SIGNAL:
            node = self.translate_to_signal(node, sp, template)

        return node



    def translate_to_signal(self, node: StatementTreeOperandNode, sp: SignalPhrase, template: dict):
        signal_templates = template["SignalTemplate"]

        if len(signal_templates) > 1:
            mergedNode = StatementTreeMergedNode(parent=node.parent)

            for signal_template in signal_templates:
                subnode = StatementTreeOperandNode(kind=None) # kind is filled by translate_node_to_signal()
                subnode = self.translate_node_to_signal(subnode, sp, signal_template)
                mergedNode.subnodes.append(subnode)

            return mergedNode

        else:
            return self.translate_node_to_signal(node, sp, template["SignalTemplate"][0])


    def translate_node_to_signal(self, node: StatementTreeOperandNode, sp: SignalPhrase, signal_template: dict):
        variable = signal_template["Template"]

        # replace all named patterns by their value
        for group, value in sp.vars.items():
            if value is not None:
                value = self.ntm.translate(value)
                # capitalize the first letter of every value inside a variable
                # note: do not use variable.capitalize(), this would make all other letters lowercase
                value = value[0].upper() + value[1:]
                strToReplace = re.compile(r"\(\?P\<{}\>[^\)]+\)".format(group))
                variable = re.sub(strToReplace, value, variable)

        # the result should be a variable name without any whitespaces
        variable = re.sub(r'\s+', '', variable)

        # make the variable camelcase - lowercase the first letter
        variable = variable[0].lower() + variable[1:]

        node.data.variable = variable

        # in case it's not edge or force, just use the template type
        if node.kind is None:
            node.kind = signal_template["Type"]


        # fill in the value
        valueId = signal_template["ValueId"]

        if node.data.value is None:
            if valueId in sp.vars:
                # should work for every template where value is stated explicitly in the NL phrase
                var = self.ntm.translate(sp.vars[valueId])
                node.data.value = var
            elif node.kind == c.BOOL:
                # default value for bool
                node.data.value = True

                if node.negated:
                    node.data.value = False
                    node.negated = False
            else:
                # TODO should not occur in practice
                # default value for everything else
                node.data.value =  1

        return node


    def translate_to_nl(self, node: StatementTreeNode, signalPhrase: SignalPhrase):
        # call Temp2NL
        fill_action = FillActions(self.nmm)
        fill_action.ParseMainAction(data=signalPhrase)

        if not signalPhrase.niceStr:
            logging.warning("niceStr not received in the response",
                            extra={"type": logging_types.W_GENERAL_ERROR, "phrase": signalPhrase})

        node.data.variableNL = signalPhrase.niceStr


    def match_compound_signal_templates(self, node: StatementTreeBinaryOperatorNode):
        # only for direction TreeProcessor.Direction.SIGNAL_TO_NL
        operands = self.gather_conjunction_operands(node)

        for template in self.templ_dic:
            if not operands or len(template["SignalTemplate"]) != len(operands):
                # number of operands do not equal number of template strings,
                # cannot match the compound template
                continue

            matched_str_idxs = []
            matches = []

            for operand in operands:
                i, match = self.match_signal_template(operand, template)

                if match:
                    matches.append(match)
                    # save the index of the matched template string
                    matched_str_idxs.append(i)

            # check if matched templates strings are unique (none was matched twice)
            # and complete (all were matched)
            if len(set(matched_str_idxs)) == len(operands):
                merged_node = StatementTreeMergedNode()
                merged_node.subnodes = operands

                return template, matches, merged_node

        return None


    def gather_conjunction_operands(self, node):
        # gathers a list of operand nodes in a subtree connected via AND operator nodes
        if node.kind == c.AND:
            left_operands = self.gather_conjunction_operands(node.lchild)
            right_operands = self.gather_conjunction_operands(node.rchild)

            if left_operands and right_operands:
                # concatenate lists from both branches
                return left_operands + right_operands

            # if one of the branches did not succeed, the whole operation failed

        elif type(node) is StatementTreeOperandNode:
            # we encountered an operand, return it as an element of a list
            return [node]

        # signalizes the operation was invalid, subtree is not a conjunction of operands
        return None




    def match_simple_templates(self, node: StatementTreeOperandNode):
        # finds a matching template in the YAML file (works for both directions)
        match = None

        for template in self.templ_dic:
            if self.dir == TreeProcessor.Direction.NL_TO_SIGNAL:
                match = self.match_nl_template(node, template)
            elif self.dir == TreeProcessor.Direction.SIGNAL_TO_NL:

                if len(template["SignalTemplate"]) > 1:
                    # here we match only simple templates
                    continue

                _, match = self.match_signal_template(node, template)

            if match:
                return match, template

        return None, None



    def match_signal_template(self, operand: StatementTreeOperandNode, template: dict):
        templates_str = template["SignalTemplate"]

        # at least one of the SignalTemplates has to match operand variable
        for i, template_str in enumerate(templates_str):
            expToMatch = re.compile(r"^{}$".format(template_str["Template"].strip()))
            match = expToMatch.search(operand.data.variable)

            if match:
                operand.data.valueId = template_str["ValueId"]
                return i, match

        # no match found
        return None, None

    def match_nl_template(self, operand: StatementTreeOperandNode, template: dict):
        templates_str = template["NLTemplateEn"
                            if self.language == c.LANG_EN
                            else "NLTemplateCz"]


        for i, template_str in enumerate(templates_str):
            expToMatch = re.compile(r"^\s*{}\s*$".format(template_str), flags=re.IGNORECASE)
            match = expToMatch.search(operand.data.variableNL)

            if match:
                return match

        return None


    def load_templ_dic(self, file):
        # load templates to be matched
        with pkg_resources.resource_stream("gherkan", file) as stream:
            try:
                self.templ_dic = yaml.full_load(stream)
            except yaml.YAMLError as exc:
                logging.exception(exc)