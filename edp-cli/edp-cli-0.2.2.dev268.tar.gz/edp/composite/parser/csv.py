import pyparsing as pp
from pyparsing import pyparsing_common


def _build_csv_parser():
    separator = pp.Suppress(':')
    key = pp.Word(pp.printables, excludeChars=':')
    value = pp.Regex(r'[^\n\r]*') + pp.LineEnd().suppress()

    block_name = key + separator  + pp.LineEnd().suppress()

    key_value = key + separator + value

    header = (pp.LineStart().suppress() +  pp.Word(pp.nums) + pp.ZeroOrMore( pp.White().suppress() + pp.Word(pp.nums)) + pp.LineEnd().suppress())

    csv_header = pp.delimitedList(pp.Word(pp.printables, excludeChars=',')) + pp.LineEnd().suppress()

    csv_row = pp.delimitedList(pp.Word(pp.nums + ';.+-e_') | pp.Literal('custom') | pp.Literal('NaN')) + pp.LineEnd().suppress()

    indent_stack = [1]
    block = pp.Forward()
    block_body = ( block | key_value)

    indented_block = pp.Dict(pp.ungroup(pp.indentedBlock(block_body, indent_stack)))
    block << ( block_name + indented_block | key_value)

    return pp.Optional(header) + pp.ZeroOrMore(pp.Dict(pp.Group(block))).setResultsName('meta') + \
        csv_header.setResultsName('csvHeader') + \
        pp.Group(pp.OneOrMore(pp.Group(csv_row))).setResultsName('csvValues')


def _to_float(s):
    try:
        return float(s)
    except ValueError:
        return s

parser = None
def parse_csv(contents):
    global parser
    if parser is None:
        parser = _build_csv_parser()

    tree = parser.parseString(contents)
    data = {}
    if 'meta' in tree:
        data = tree['meta'].asDict()
    csv_headers = tree['csvHeader']
    csv_values = tree['csvValues']

    for i, header in enumerate(csv_headers):
        if header == 'sample_no':
            data[header]  = [int(row[i]) for row in csv_values]
        else:
            data[header] = [_to_float(row[i]) for row in csv_values]

    return data
