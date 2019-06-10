import pyparsing as pp
from pyparsing import pyparsing_common


def _build_exp_parser():
    separator = pp.Suppress(':')
    key = pp.Word(pp.printables, excludeChars=':')
    value = pp.Regex(r'[^\n\r:]+') + pp.LineEnd().suppress()

    block_name = key + separator  + pp.LineEnd().suppress()
    run_block_name = pp.Regex(r'run__[\d]+') + separator  + pp.LineEnd().suppress()
    platemap_keylist = pp.Literal('platemap_comp4plot_keylist') + separator +  pp.delimitedList(pp.Word(pp.alphas))
    run_ids = pp.Literal('run_ids') + separator +  pp.delimitedList(pyparsing_common.integer)
    plate_ids = (pp.Literal('plate_ids') | pp.Literal('plate_id'))  + separator +  pp.delimitedList(pyparsing_common.integer)

    key_value = (
        platemap_keylist | run_ids | plate_ids |
        key + separator + value
    )

    indent_stack = [1]
    block = pp.Forward()
    block_body = ( block | key_value)

    indented_block = pp.Dict(pp.ungroup(pp.indentedBlock(block_body, indent_stack)))
    block << ( block_name + indented_block | key_value)

    # run block
    run_block = run_block_name + indented_block

    return pp.OneOrMore(pp.Dict(pp.Group(key_value))) + pp.Group(pp.OneOrMore(pp.Dict(pp.Group(run_block)))).setResultsName('runs')


def parse_exp(contents):
    parser = _build_exp_parser()
    tree = parser.parseString(contents)
    runs = tree['runs']
    del tree['runs']
    run_list = []

    for run in  runs:
        run_key = run[0]
        run = run.asDict()
        run['run_key'] = run_key
        run_list.append(run)

    d = tree.asDict()
    d['runs'] = run_list

    return d
