from lib5c.tools.parents import parallelization_parser, simple_in_out_parser, \
    primerfile_parser


def add_log_tool(parser):
    log_parser = parser.add_parser(
        'log',
        prog='lib5c log',
        help='log countsfiles',
        parents=[primerfile_parser, parallelization_parser,
                 simple_in_out_parser]
    )
    log_parser.add_argument(
        '-b', '--log_base',
        type=str,
        default='e',
        help='''Specify what base to use when logging. The default is 'e' for
        natural log.''')
    log_parser.add_argument(
        '-s', '--pseudocount',
        type=float,
        default=1.0,
        help='''The pseudocount to add before logging. The default is 1.0.''')
    log_parser.add_argument(
        '-U', '--unlog',
        action='store_true',
        help='''Pass this flag to unlog instead of logging.''')
    log_parser.set_defaults(func=log_tool)


def log_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import parallel_log_counts, parallel_unlog_counts
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    resolve_parallel(parser, args, subcommand='log')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # resolve base
    resolved_base = args.log_base
    if resolved_base not in ['e', '2', '10']:
        resolved_base = float(resolved_base)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # divide
    if args.unlog:
        print('unlogging counts')
        counts = parallel_unlog_counts(counts, pseudocount=args.pseudocount,
                                       base=resolved_base)
    else:
        print('logging counts')
        counts = parallel_log_counts(counts, pseudocount=args.pseudocount,
                                     base=resolved_base)

    # write output
    print('writing counts')
    write_counts(counts, args.outfile, primermap)
