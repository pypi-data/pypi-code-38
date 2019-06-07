from lib5c.tools.parents import parallelization_parser, simple_in_out_parser, \
    primerfile_parser


def add_qvalues_tool(parser):
    qvalues_parser = parser.add_parser(
        'qvalues',
        prog='lib5c qvalues',
        help='perform multiple testing correction',
        parents=[primerfile_parser, parallelization_parser,
                 simple_in_out_parser]
    )
    qvalues_parser.add_argument(
        '-m', '--method',
        type=str,
        default='fdr_bh',
        help='''Specify what method to use for multiple testing correction. Must
        be supported by `statsmodels.stats.multitest.multipletests()` The
        default is 'fdr_bh' for Benjamini-Hochberg.''')
    qvalues_parser.set_defaults(func=qvalues_tool)


def qvalues_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.statistics import adjust_pvalues
    from lib5c.util.counts import apply_nonredundant
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    resolve_parallel(parser, args, subcommand='qvalues')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading pvalues')
    primermap = load_primermap(primerfile)
    pvalues = load_counts(args.infile, primermap)

    # mtc
    print('performing multiple testing correction')
    qvalues = apply_nonredundant(
        lambda x: adjust_pvalues(x, method=args.method), pvalues, primermap)

    # write output
    print('writing counts')
    write_counts(qvalues, args.outfile, primermap)
