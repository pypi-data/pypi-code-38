from lib5c.tools.parents import parallelization_parser, log_vs_vst_parser, \
    primerfile_parser


def add_pvalues_tool(parser):
    pvalues_parser = parser.add_parser(
        'pvalues',
        prog='lib5c pvalues',
        help='call pvalues for interactions',
        parents=[primerfile_parser, parallelization_parser, log_vs_vst_parser]
    )
    pvalues_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts for which p-values should be
        called.''')
    pvalues_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    pvalues_parser.add_argument(
        'variance',
        type=str,
        help='''File containing variance counts.''')
    pvalues_parser.add_argument(
        'distribution',
        choices=['poisson', 'nbinom', 'norm', 'logistic'],
        help='''The distribution to use to call p-values.''')
    pvalues_parser.add_argument(
        'outfile',
        type=str,
        help='''Path to file to write p-value counts to.''')
    pvalues_parser.set_defaults(func=pvalues_tool)


def pvalues_tool(parser, args):
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.util.distributions import call_pvalues
    from lib5c.util.counts import parallel_log_counts

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='pvalues', key_arg='observed')
    primerfile = resolve_primerfile(args.observed, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)
    variance_counts = load_counts(args.variance, primermap)

    # honor log vs vst
    if args.log or args.vst:
        observed_counts = parallel_log_counts(observed_counts)
    if args.vst:
        expected_counts = parallel_log_counts(expected_counts)

    # fit distributions
    print('calling pvalues')
    pvalues = call_pvalues(observed_counts, expected_counts, variance_counts,
                           args.distribution, log=args.log)

    # write p-values
    print('writing p-values')
    write_counts(pvalues, args.outfile, primermap)
