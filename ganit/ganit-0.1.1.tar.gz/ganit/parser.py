from .handle_invalid_scenarios import ParserError
from .prescan import pre_scan
from .converter import convert
from .evaluator import evaluate
from .utils import *
class Parser:
    def prescan(self, exp):
        try:
            if isinstance(exp, dict):
                expr = exp.get("exp")
                exp = expr
            if exp is None:
                raise ParserError("Empty Expression")
            return pre_scan(exp)
        except ParserError as e:
            raise e

    def convert(self, exp, variables=None):
        try:
            if isinstance(exp, dict):
                expr = exp.get("exp")
                variables = exp.get("variables", None)
                exp = expr

            prescanned = self.prescan(exp)
            if variables is None:
                postfix = convert(prescanned, None)
            else:
                postfix = convert(prescanned, variables)
            return postfix
        except ParserError as e:
            raise e

    def evaluate(self, exp, convert=True, variables=None):
        try:
            if isinstance(exp, dict):
                expr = exp.get("exp")
                variables = exp.get("variables", None)
                convert = exp.get("convert", None)
                exp = expr
            if isinstance(convert, dict):
                variables = convert
                convert = True
            if convert is None or convert==True:
                postfix = self.convert(exp, variables)
            else:
                postfix = exp

            result = evaluate(postfix, variables)
            #print(result)
            if isinstance(result, bool):
                return result
            if is_int(result):
                return int(result)
            elif is_float(result):
                return float(result)
            else:
                return result
        except ParserError as e:
            raise e
