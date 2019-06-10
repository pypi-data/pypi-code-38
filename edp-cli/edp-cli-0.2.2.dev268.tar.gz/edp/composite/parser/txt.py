import pyparsing as pp
from pyparsing import pyparsing_common


def _build_txt_parser():
    separator = pp.Suppress('=')
    key = pp.Literal('%')  + pp.Word(pp.printables, excludeChars='=')
    value = pp.Regex(r'[^\n\r]*') + pp.LineEnd().suppress()

    key_value = key + separator + value

    header = (pp.LineStart().suppress() +  pp.Word(pp.nums) + pp.ZeroOrMore( pp.White().suppress() + pp.Word(pp.nums)) + pp.LineEnd().suppress())

    column_heading =  pp.Literal('%')  + pp.Word(pp.printables, excludeChars='=') + separator + value
    
    txt_row = pp.delimitedList(pp.Word(pp.nums + '.+-e_') | pp.Literal('custom')) + pp.LineEnd().suppress()

    return pp.Optional(header) + pp.ZeroOrMore(pp.Dict(pp.Group(block))).setResultsName('meta') + \
        column_heading.setResultsName('columnHeading') + \
        pp.Group(pp.OneOrMore(pp.Group(csv_row))).setResultsName('textValues')


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
