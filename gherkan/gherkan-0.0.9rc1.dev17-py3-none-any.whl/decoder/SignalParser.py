# -*- coding: utf-8 -*-
from gherkan.containers.StatementTree import StatementTree
from gherkan.decoder.Parser import Parser

from lark import Lark
from gherkan.utils import gherkin_keywords as g

class SignalParser(Parser):
    def __init__(self):
        super().__init__()

        self.statement_grammar = """
            ?start: expression

            ?expression: statement
                | "(" expression ")"
                | expression "&&" expression       -> and
                | expression "||" expression       -> or
                | "!" "(" expression ")"           -> not

            ?statement: function
                | NAME "==" atom                -> equality
                | NAME "!=" atom                -> inequality
                | NAME                          -> bool
                | "!" statement                 -> not

            ?function: function_name "(" NAME "," atom ")"

            ?function_name: "edge"           -> edge 
                          | "force"          -> force
                          | "unforce"        -> unforce
            
            ?atom: NAME
                | NUMBER

            %import common.CNAME -> NAME
            %import common.NUMBER
            %import common.WS_INLINE

            %ignore WS_INLINE
        """


    def parseStatement(self, statement: str, negate=False):
        parser = Lark(self.statement_grammar, parser='earley', ambiguity='resolve', propagate_positions=True)
        tree = parser.parse(statement)

        # print(tree.pretty())

        st = StatementTree(statement)
        st.buildFromSignalTree(tree, negate)

        # print(st)

        return st

    def mergeAndSections(self, textlines: list, sectionList: list):
        """
        Naïve approach for parsing "And" sections. Find the lines with "And" sections and merge their statements
        with the previous line by "&&" operator.
        """
        for lineNumber, section in sectionList:
            if section == g.AND:
                statement = self.getTextAfterKeyword(textlines[lineNumber]).group("result")
                textlines[lineNumber - 1] += " && {}".format(statement)
                textlines[lineNumber] = ""

        return textlines

    def setNegateSignal(self):
        self.negate_signal = True