from lib5c.tools.parents import parallelization_parser, region_parser, \
    log_vs_vst_parser, donut_parser, expected_selection_parser, lim_parser, \
    primerfile_parser


def add_visualize_variance_tool(parser):
    visualize_variance_parser = parser.add_parser(
        'visualize-variance',
        prog='lib5c plot visualize-variance',
        help='visualize variance estimates',
        parents=[primerfile_parser, parallelization_parser, region_parser,
                 log_vs_vst_parser, donut_parser, expected_selection_parser,
                 lim_parser]
    )
    visualize_variance_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    visualize_variance_parser.add_argument(
        'variance',
        type=str,
        help='''File containing variance counts.''')
    visualize_variance_parser.add_argument(
        '-o', '--observed',
        type=str,
        help='''File containing observed counts. Pass this to treat "variance"
        as containing a fitted variance values, and to recompute raw variance
        values from the observed and expected to compare with the fitted
        values. The raw variance estimates are controlled by -V, -n, and -f, see
        "lib5c variance --help" for details.''')
    visualize_variance_parser.add_argument(
        '-S', '--scatter',
        action='store_true',
        help='''Pass this flag to force plotting exp vs var as a scatterplot
        when obs is not passed. By default it will be a line plot.''')
    visualize_variance_parser.add_argument(
        '-B', '--hexbin',
        action='store_true',
        help='''Pass this flag in combination with -S/--scatter to replace the
        scatterplot with a hexbin plot. Not compatible with
        -O/--overlay_regions.''')
    visualize_variance_parser.add_argument(
        '-G', '--global_mvr',
        action='store_true',
        help='''Pass this flag to show mean-variance trends from a global
        perspective, combining data from all regions.''')
    visualize_variance_parser.add_argument(
        '-O', '--overlay_regions',
        action='store_true',
        help='''Pass this flag to overlay MVRs across regions rather than
        plotting each region in a separate plot.''')
    visualize_variance_parser.add_argument(
        '-T', '--trim_limits',
        action='store_true',
        help='''If -o/--observed is passed, pass this flag to trim the x- and
        y-limits to the range of the group expected and variance values.
        Overridden by -x/-y. Doesn't work with -O/--overlay_regions.''')
    visualize_variance_parser.add_argument(
        '--logx',
        action='store_true',
        help='''Pass this flag to draw the x-axis on a log-scale.''')
    visualize_variance_parser.add_argument(
        '--logy',
        action='store_true',
        help='''Pass this flag to draw the y-axis on a log-scale.''')
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
    from lib5c.plotters.variance import plot_mvr, plot_mvr_parallel,\
        plot_overlay_mvr

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.expected, args.primerfile)
    resolve_parallel(parser, args, subcommand='plot visualize-variance',
                     key_arg='expected')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = None
    expected_counts = load_counts(args.expected, primermap)
    variance_counts = load_counts(args.variance, primermap)
    if args.observed:
        observed_counts = load_counts(args.observed, primermap)
        if args.region is not None:
            observed_counts = observed_counts[args.region]

    # resolve region and outfile
    if args.region is not None:
        expected_counts = expected_counts[args.region]
        variance_counts = variance_counts[args.region]
        resolved_outfile = args.outfile
    else:
        if not args.overlay_regions and not args.global_mvr:
            resolved_outfile = {region: args.outfile.replace(r'%r', region)
                                for region in expected_counts.keys()}
        else:
            resolved_outfile = args.outfile

    # resolve xlim and ylim
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else None
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # resolve plotting function
    if args.global_mvr:
        plot_fn = plot_mvr
    elif args.overlay_regions:
        plot_fn = plot_overlay_mvr
    else:
        plot_fn = plot_mvr_parallel

    # fit and plot
    print('plotting')
    plot_fn(
        expected_counts, variance_counts, obs=observed_counts,
        num_groups=args.num_groups,
        group_fractional_tolerance=args.group_fractional_tolerance,
        exclude_offdiagonals=args.exclude_offdiagonals,
        log=args.log, logx=args.logx, logy=args.logy, vst=args.vst,
        scatter=args.scatter, hexbin=args.hexbin, trim_limits=args.trim_limits,
        outfile=resolved_outfile, xlim=xlim, ylim=ylim)
