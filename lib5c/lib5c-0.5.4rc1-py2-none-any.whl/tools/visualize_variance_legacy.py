from lib5c.tools.parents import parallelization_parser, distribution_parser,\
    region_parser, primerfile_parser


def add_visualize_variance_tool(parser):
    visualize_variance_parser = parser.add_parser(
        'visualize-variance',
        help='visualize variance estimates',
        parents=[primerfile_parser, parallelization_parser, distribution_parser,
                 region_parser]
    )
    visualize_variance_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts for which p-values should be
        called.''')
    visualize_variance_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    visualize_variance_parser.add_argument(
        'outfile',
        type=str,
        help='''File to save variance plots to. %%r in the filename will be
        replaced with the region name.''')
    visualize_variance_parser.set_defaults(func=visualize_variance_tool)


def visualize_variance_tool(parser, args):
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.variance_legacy import fit_and_plot

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.observed, args.primerfile)
    resolve_parallel(parser, args, subcommand='visualize-variance',
                     key_arg='observed')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)

    # resolve region
    if args.region is not None:
        observed_counts = observed_counts[args.region]
        expected_counts = expected_counts[args.region]
        resolved_region = args.region
        resolved_outfile = args.outfile
    else:
        resolved_region = {region: region for region in observed_counts.keys()}
        resolved_outfile = {region: args.outfile.replace(r'%r', region)
                            for region in observed_counts.keys()}

    # fit and plot
    print('fitting and plotting')
    fit_and_plot(resolved_outfile, observed_counts, expected_counts,
                 resolved_region, mode=args.mode, dist=args.distribution,
                 log=args.log)
