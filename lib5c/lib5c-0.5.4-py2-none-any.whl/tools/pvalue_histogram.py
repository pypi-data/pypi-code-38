from lib5c.tools.parents import parallelization_parser, lim_parser, \
    primerfile_parser


def add_pvalue_histogram_tool(parser):
    pvalue_histogram_parser = parser.add_parser(
        'pvalue-histogram',
        prog='lib5c plot pvalue-histogram',
        help='draw histograms of pvalues',
        parents=[primerfile_parser, parallelization_parser, lim_parser]
    )
    pvalue_histogram_parser.add_argument(
        '-B', '--bh_fdr',
        action='store_true',
        help='''Pass this flag to apply BH-FDR adjustment to p-values.''')
    pvalue_histogram_parser.add_argument(
        '-T', '--two_tail',
        action='store_true',
        help='''Convert one-tail p-values to two-tail p-values before
        plotting.''')
    pvalue_histogram_parser.add_argument(
        'pvalues',
        type=str,
        help='''Countsfile containing pvalues to histogram.''')
    pvalue_histogram_parser.add_argument(
        'outfile',
        type=str,
        help='''File to save histogram to.''')
    pvalue_histogram_parser.set_defaults(func=pvalue_histogram_tool)


def pvalue_histogram_tool(parser, args):
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import flatten_counts_to_list
    from lib5c.util.system import check_outdir
    from lib5c.util.plotting import adjust_plot, DEFAULT_RC
    from lib5c.util.statistics import adjust_pvalues, convert_to_two_tail

    # resolve primerfile and parallel
    resolve_parallel(parser, args, subcommand='plot pvalue-histogram',
                     key_arg='pvalues')
    primerfile = resolve_primerfile(args.pvalues, args.primerfile)

    # load and flatten counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    pvalue_counts = load_counts(args.pvalues, primermap)
    pvalues = flatten_counts_to_list(pvalue_counts, discard_nan=True)
    if args.two_tail:
        pvalues = convert_to_two_tail(pvalues)
    if args.bh_fdr:
        pvalues = adjust_pvalues(pvalues)

    # resolve plot_kwargs
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else [0, 1]
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # check outdir
    check_outdir(args.outfile)

    # plot
    sns.set(color_codes=True)
    with sns.axes_style('ticks', DEFAULT_RC):
        plt.hist(pvalues, bins=np.linspace(0, 1, 101))

    # adjust plot
    adjust_plot(xlim=xlim, ylim=ylim)

    # save
    plt.savefig(args.outfile, bbox_inches='tight')
