from gherkin.parser import Parser
from gherkin.pickles.compiler import compile

from pprint import pprint as pp
import gherkan.utils.constants as c
import os

# requires 'gherkin-official' package
parser = Parser()
input_file = os.path.join(c.DATA_DIR, "input", "test_R1NormalSequence_signals.feature")

with open(input_file, "rt", encoding="utf-8") as file:
    lines = file.read()

    gherkin_document = parser.parse(lines)
    pickles = compile(gherkin_document)

    pp(pickles)