from lib5c.tools.parents import parallelization_parser, donut_parser, \
    log_vs_vst_parser, expected_selection_parser, lim_parser, primerfile_parser


def add_visualize_fits_tool(parser):
    visualize_fits_parser = parser.add_parser(
        'visualize-fits',
        prog='lib5c plot visualize-fits',
        help='visualize fits across distributions and approaches',
        parents=[primerfile_parser, parallelization_parser, donut_parser,
                 log_vs_vst_parser, expected_selection_parser, lim_parser]
    )
    visualize_fits_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts.''')
    visualize_fits_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    visualize_fits_parser.add_argument(
        'variance',
        type=str,
        help='''File containing variance counts.''')
    visualize_fits_parser.add_argument(
        'distribution',
        choices=['poisson', 'nbinom', 'norm', 'logistic'],
        help='''The distribution to show the fit of.''')
    visualize_fits_parser.add_argument(
        'target',
        type=float,
        help='''The target expected value around which the fit should be
        drawn.''')
    visualize_fits_parser.add_argument(
        'region',
        type=str,
        help='''The region to consider.''')
    visualize_fits_parser.add_argument(
        'outfile',
        type=str,
        help='''File to save plotted fits to.''')
    visualize_fits_parser.set_defaults(func=visualize_fits_tool)


def visualize_fits_tool(parser, args):
    import numpy as np
    import scipy.stats as stats
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.fits import plot_group_fit
    from lib5c.util.distributions import freeze_distribution

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.observed, args.primerfile)
    resolve_parallel(parser, args, subcommand='plot visualize-fits',
                     key_arg='observed')

    # resolve dist_gen
    dist_gen = getattr(stats, args.distribution)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_matrix = load_counts(args.observed, primermap)[args.region]
    expected_matrix = load_counts(args.expected, primermap)[args.region]
    variance_matrix = load_counts(args.variance, primermap)[args.region]

    # resolve target indices
    flat_idx = np.nanargmin(np.abs(expected_matrix - args.target))
    i, j = flat_idx / len(expected_matrix), flat_idx % len(expected_matrix)

    # honor vst
    if args.vst:
        observed_matrix = np.log(observed_matrix + 1)
        expected_matrix = np.log(expected_matrix + 1)

    # freeze distribution
    frozen_dist = freeze_distribution(dist_gen, expected_matrix[i, j],
                                      variance_matrix[i, j], log=args.log)

    # resolve xlim and ylim
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else None
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # fit and plot
    print('plotting')
    plot_group_fit(
        observed_matrix, expected_matrix, i, j, frozen_dist,
        local=args.donut, p=args.donut_inner_size, w=args.donut_outer_size,
        group_fractional_tolerance=args.group_fractional_tolerance,
        vst=args.vst, log=args.log, outfile=args.outfile, xlim=xlim, ylim=ylim)
