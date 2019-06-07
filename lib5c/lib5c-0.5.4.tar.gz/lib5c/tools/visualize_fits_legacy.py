from lib5c.tools.parents import parallelization_parser, distribution_parser,\
    region_parser, primerfile_parser


def add_visualize_fits_tool(parser):
    visualize_fits_parser = parser.add_parser(
        'visualize-fits',
        help='visualize fits across distributions and approaches',
        parents=[primerfile_parser, parallelization_parser, distribution_parser,
                 region_parser]
    )
    visualize_fits_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts for which p-values should be
        called.''')
    visualize_fits_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    visualize_fits_parser.add_argument(
        'outfile',
        type=str,
        help='''File to save plotted fits to. %%r in the filename will be
        replaced with the region name. %%e in the filename will be replaced with
        the expected value, unless only one fit is to be used for all expected
        values, or unless the expected value is specified by the -s or -e
        flags.''')
    visualize_fits_parser.add_argument(
        '-s', '--distance_scale',
        type=int,
        help='''Specific distance (in bp) for which to plot fits if -m/--mode is
        regional_shifted, log_log_fit, or obs_over_exp. The appropriate expected
        value will be interpolated from the supplied expecetd model.''')
    visualize_fits_parser.add_argument(
        '-e', '--expected_value',
        type=float,
        help='''Specific expected value to plot fits for if -m/--mode is
        regional_shifted, log_log_fit, or obs_over_exp.''')
    visualize_fits_parser.add_argument(
        '-t', '--tolerance',
        type=float,
        default=0.5,
        help='''Tolerance for expected values to include when plotting fits if
        -m/--mode is log_log_fit or obs_over_exp. The default is 0.5.''')
    visualize_fits_parser.set_defaults(func=visualize_fits_tool)


def visualize_fits_tool(parser, args):
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.fits_legacy import fit_and_plot
    from lib5c.algorithms.expected import interpolate_expected

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.observed, args.primerfile)
    resolve_parallel(parser, args, subcommand='visualize-fits',
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
        primermap = primermap[args.region]
        resolved_region = args.region
        resolved_outfile = args.outfile
    else:
        resolved_region = {region: region for region in observed_counts.keys()}
        resolved_outfile = {region: args.outfile.replace(r'%r', region)
                            for region in observed_counts.keys()}

    # resolve expected value
    if args.distance_scale is not None:
        resolved_expected = interpolate_expected(expected_counts, primermap,
                                                 args.distance_scale)
    elif args.expected_value is not None:
        resolved_expected = args.expected_value
    else:
        resolved_expected = None

    # fit and plot
    print('fitting and plotting')
    fit_and_plot(resolved_outfile, observed_counts, expected_counts,
                 resolved_region, mode=args.mode, dist=args.distribution,
                 log=args.log, expected_value=resolved_expected,
                 tol=args.tolerance)
