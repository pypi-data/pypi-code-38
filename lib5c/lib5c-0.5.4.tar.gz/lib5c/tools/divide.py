from lib5c.tools.parents import parallelization_parser, primerfile_parser


def add_divide_tool(parser):
    divide_parser = parser.add_parser(
        'divide',
        prog='lib5c divide',
        help='divide countsfiles',
        parents=[primerfile_parser, parallelization_parser]
    )
    divide_parser.add_argument(
        'dividend',
        type=str,
        help='''Countsfile to divide, or a glob-expandable string to divide
        multiple countsfiles in parallel.''')
    divide_parser.add_argument(
        'divisor',
        type=str,
        help='''Countsfile to divide by, or a pattern containing %%s which will
        be replaced by the replicate name if multiple countsfiles are specified
        in dividend.''')
    divide_parser.add_argument(
        'quotient',
        type=str,
        help='''Countsfile to write output to, or a pattern containing %%s which
        will be replaced by the replicate name if multiple countsfiles are
        specified in dividend.''')
    divide_parser.set_defaults(func=divide_tool)


def divide_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import parallel_divide_counts
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.dividend, args.primerfile)
    resolve_parallel(parser, args, subcommand='divide', key_arg='dividend')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    dividend = load_counts(args.dividend, primermap)
    divisor = load_counts(args.divisor, primermap)

    # divide
    print('dividing counts')
    quotient = parallel_divide_counts(dividend, divisor)

    # write output
    print('writing counts')
    write_counts(quotient, args.quotient, primermap)
