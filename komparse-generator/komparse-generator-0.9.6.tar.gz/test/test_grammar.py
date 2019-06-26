import sys
import os.path
srcdir = os.path.dirname(__file__) + os.path.sep + ".." + os.path.sep + "src"
sys.path.insert(0, srcdir)

from komparse import Parser
from komparse_gen.grammar import Grammar
from komparse_gen.generator import Generator

def read_file_content(filepath):
    content = ""
    fp = open(filepath, "r")
    lines = fp.readlines()
    fp.close()
    for line in lines:
        content += line
    return content

grammar_source = read_file_content("bollang.komparse")
parser = Parser(Grammar())
ast = parser.parse(grammar_source)
if ast:
    #print(ast.to_xml())
    generator = Generator()
    generator.generate(grammar_source, 'Bollang')
else:
    print(parser.error())
    