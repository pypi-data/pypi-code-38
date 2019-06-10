import pyparsing as pp
from pyparsing import pyparsing_common
import json
import sys
import os
import errno


def _build_rawlen_parser():
    header = pp.Group(pp.LineStart().suppress() +  pp.Word(pp.printables) +
              pp.ZeroOrMore( pp.White(ws='\t ').suppress() + pp.Word(pp.printables)))

    row = (pp.LineStart().suppress() +  pp.Word(pp.nums + '.+-e_') +
           pp.ZeroOrMore(pp.White(ws='\t ').suppress() + pp.Word(pp.nums + '.+-e_')))

    return header.setResultsName('header') + \
        pp.Group(pp.OneOrMore(pp.Group(row))).setResultsName('values')

def _to_float(s):
    try:
        return float(s)
    except ValueError:
        return s
parser = None
def parse_rawlen(contents):
    global parser
    if parser is None:
        parser = _build_rawlen_parser()
    tree = parser.parseString(contents)
    header = tree['header']
    values = tree['values']
    data = {}
    for i, h in enumerate(header):
        data[h] = [_to_float(row[i]) for row in values]

    return data
