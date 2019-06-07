from lib5c.tools.parents import level_parser, parallelization_parser, \
    primerfile_parser


def add_subtract_tool(parser):
    subtract_parser = parser.add_parser(
        'subtract',
        prog='lib5c subtract',
        help='subtract countsfiles',
        parents=[primerfile_parser, level_parser, parallelization_parser]
    )
    subtract_parser.add_argument(
        'minuend',
        type=str,
        help='''Countsfile to subtract from, or a glob-expandable string to
        subtract from multiple countsfiles in parallel.''')
    subtract_parser.add_argument(
        'subtrahend',
        type=str,
        help='''Countsfile to subtract, or a pattern containing %%s which will
        be replaced by the replicate name if multiple countsfiles are specified
        in minuend.''')
    subtract_parser.add_argument(
        'difference',
        type=str,
        help='''Countsfile to write output to, or a pattern containing %%s which
        will be replaced by the replicate name if multiple countsfiles are
        specified in minuend.''')
    subtract_parser.set_defaults(func=subtract_tool)


def subtract_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import parallel_subtract_counts
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.minuend, args.primerfile)
    resolve_parallel(parser, args, subcommand='subtract', key_arg='minuend')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    minuend = load_counts(args.minuend, primermap)
    subtrahend = load_counts(args.subtrahend, primermap)

    # subtract
    print('subtracting counts')
    difference = parallel_subtract_counts(minuend, subtrahend)

    # write output
    print('writing counts')
    write_counts(difference, args.difference, primermap)
