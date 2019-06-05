# -*- coding: utf-8 -*-
from gherkan.containers.StatementTree import StatementTree
from gherkan.decoder.Parser import Parser

from lark import Lark, Token
from gherkan.utils import constants as c
from gherkan.utils import gherkin_keywords as g

import logging

class NLParser(Parser):
    def __init__(self):
        super().__init__()

        self.statement_grammar = """
            ?start: expression

            ?expression: statement
                | "(" expression ")"
                | expression "{AND}" expression      -> and
                | expression "{OR}" expression       -> or
            
            ?statement: /((?!{AND}|{OR}).)+/
            
            %import common.WS_INLINE
            %ignore WS_INLINE
        """

    def determineGrammarByLanguage(self):
        if self.language == c.LANG_EN:
            self.statement_grammar = self.statement_grammar.format(AND="AND", OR="OR")
        elif self.language == c.LANG_CZ:
            self.statement_grammar = self.statement_grammar.format(AND="A", OR="NEBO")
        else:
            logging.error("Language {} not recognized", self.language)


    def mergeAndSections(self, textlines: list, sectionList: list):
        """
        Naïve approach for parsing "And" sections. Find the lines with "And" sections and merge their statements
        with the previous line by "&&" operator.
        """
        for lineNumber, section in sectionList:
            if section == g.AND:
                statement = self.getTextAfterKeyword(textlines[lineNumber]).group("result")
                textlines[lineNumber - 1] += " {} {}".format(g.get_kw(self.language, "And").upper(), statement)
                textlines[lineNumber] = ""

        return textlines

    def parseStatement(self, statement: str, negate=False):
        if negate:
            logging.error("Negate option not implemented for NL")

        self.determineGrammarByLanguage()

        parser = Lark(self.statement_grammar, parser='earley', ambiguity='resolve', propagate_positions=True)
        tree = parser.parse(statement)

        # if type(tree) == Token:
        #     print(tree)
        # else:
        #     print(tree.pretty())

        st = StatementTree(statement)
        st.buildFromNLTree(tree)
        
        # print(st)

        return st
