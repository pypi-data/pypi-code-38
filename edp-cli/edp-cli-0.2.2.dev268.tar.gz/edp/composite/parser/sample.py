import pyparsing as pp
from pyparsing import pyparsing_common


def _build_sample_parser():
    separator = pp.Suppress('=')
    key = pp.LineStart() + pp.Literal('%').suppress() + pp.Word(pp.printables, excludeChars='=')
    value =  pp.Regex(r'[^\r%]*') | pp.Empty() + pp.LineEnd().suppress()

    element = pp.Word(pp.alphas)
    elements = pp.Group(pp.LineStart().suppress() + pp.Literal('%').suppress()  +
                pp.Literal('elements') + separator + element +
                pp.ZeroOrMore( pp.White(ws='\t ').suppress() + element) +
                pp.LineEnd().suppress())

    compositions = pp.Group(pp.LineStart().suppress() + pp.Literal('%').suppress()  +
                pp.Literal('compositions') + separator + pyparsing_common.number +
                pp.ZeroOrMore( pp.White(ws='\t ').suppress() + pyparsing_common.number) +
                pp.LineEnd().suppress())

    epoch = pp.Group(pp.LineStart().suppress() + pp.Literal('%').suppress()  +
                pp.Literal('Epoch') + separator + pyparsing_common.number +
                pp.LineEnd().suppress())

    sample = pp.Group(pp.LineStart().suppress() + pp.Literal('%').suppress()  +
                pp.Literal('Sample') + separator + pyparsing_common.number +
                pp.LineEnd().suppress())

    key_value = (
        sample | epoch | elements | compositions |
        pp.Group(key + separator + value)
    )

    row_separator = pp.White(ws='\t ').suppress()
    row = (pp.LineStart().suppress() +  pyparsing_common.number +
           pp.ZeroOrMore( row_separator + pyparsing_common.number) + pp.LineEnd().suppress())

    return  pp.OneOrMore(pp.Dict(key_value)).setResultsName('meta') + \
        pp.Group(pp.ZeroOrMore(pp.Group(row))).setResultsName('values')

parser = None
def parse_sample(contents):
    global parser
    if parser is None:
        parser = _build_sample_parser()

    tree = parser.parseString(contents)

    data = tree['meta'].asDict()
    column_headings = data['column_headings'].split()
    del data['column_headings']
    values = tree['values']

    for i, header in enumerate(column_headings):
        data[header] = [float(row[i]) for row in values]

    return data
