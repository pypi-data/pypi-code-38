from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, primerfile_parser


def add_expected_tool(parser):
    expected_parser = parser.add_parser(
        'expected',
        prog='lib5c expected',
        help='compute expected models',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    expected_parser.add_argument(
        '-G', '--global_expected',
        action='store_true',
        help='''Pass this flag to use a global 1-D distance expected instead of
        a regional one.''')
    expected_parser.add_argument(
        '-M', '--force_monotonic',
        action='store_true',
        help='''Force the 1-D distance dependence to be monotonic.''')
    expected_parser.add_argument(
        '-E', '--exclude_near_diagonal',
        action='store_true',
        help='''If -R/--regression or -L/--lowess is passed and the data is
        bin-level, pass this flag to exclude the first 1/3 of the distance
        scales from the fitting operation.''')
    group_prl = expected_parser.add_mutually_exclusive_group()
    group_prl.add_argument(
        '-P', '--powerlaw',
        action='store_true',
        help='''Fit a discrete power law distribution to distances counts are
        detected at. This ignores -t.''')
    group_prl.add_argument(
        '-R', '--regression',
        action='store_true',
        help='''Fit a log-log polynomial regression to the 1-D distance
        dependence. This forces -t both. The degree of the polynomial can be
        specified with the -d/--degree flag.''')
    group_prl.add_argument(
        '-L', '--lowess',
        action='store_true',
        help='''Pass this flag to lowess smooth the 1-D distance dependence.''')
    expected_parser.add_argument(
        '-d', '--degree',
        type=int,
        default=1,
        help='''This flag sets the degree of the polynomial used for regression
        when the -R flag is passed. The default is 1 for a linear fit.''')
    expected_parser.add_argument(
        '-f', '--smoothing_fraction',
        type=float,
        default=0.8,
        help='''The fraction of the data to use when lowess smoothing. The
        default is 0.8.''')
    expected_parser.add_argument(
        '-D', '--donut_correction',
        action='store_true',
        help='''Pass this flag to use the local donut correction factor.''')
    expected_parser.add_argument(
        '-w', '--donut_outer_size',
        type=int,
        default=15,
        help='''The outer size of the donut to use. The default is 15.''')
    expected_parser.add_argument(
        '-x', '--donut_inner_size',
        type=int,
        default=5,
        help='''The inner size of the donut to use. The default is 5.''')
    expected_parser.add_argument(
        '-m', '--minimum_donut_fraction',
        type=float,
        default=0.2,
        help='''The minimum fraction of the donut that must be occupied by real
        values. Default is 0.2.''')
    expected_parser.add_argument(
        '-e', '--min_exp',
        type=float,
        default=0.1,
        help='''When passing -D/--donut_correction, if the sum of the expected
        values under the donut footprint for a particular pixel is less than
        this value, the output at this pixel will be set to nan to avoid
        numerical instability related to division by small numbers. Default is
        0.1.''')
    expected_parser.add_argument(
        '-O', '--log_donut',
        action='store_true',
        help='''When using the -D/--donut_correction flag, additionally pass
        this flag to perform the dount correction in log space.''')
    expected_parser.add_argument(
        '-X', '--max_with_lower_left',
        action='store_true',
        help='''When using the -D/--donut_correction flag, additionally pass
        this flag to use the max of the donut and the lower left as the local
        correction factor.''')
    expected_parser.add_argument(
        '-t', '--log_transform',
        type=str,
        choices=['both', 'counts', 'none', 'auto'],
        default='auto',
        help='''Determines which quantities should be logged when performing
        expected modeling. Pass 'both' to log both counts and distances. Pass
        'counts' to log only the counts. Pass 'none' to log neither quantity.
        The default is 'auto', which uses a sane default that depends on the
        other parameters. This flag may be forced by other paramters.''')
    expected_parser.add_argument(
        '-o', '--plot_outfile',
        type=str,
        help='''Pass a string reference to a path to which to write
        visualizations of the 1-D expected model. This string should include one
        %%r, which will be replaced with the region name. A %%d in this string
        will be replaced with the output directory of the countsfiles.''')
    expected_parser.add_argument(
        '-K', '--kde',
        action='store_true',
        help='''Use a kernel density estimate instead of a scatterplot when
        plotting the visualization.''')
    expected_parser.add_argument(
        '-B', '--hexbin',
        action='store_true',
        help='''Use hexagonal bins instead of a scatterplot when plotting the
        visualization.''')
    expected_parser.add_argument(
        '-S', '--single_model',
        action='store_true',
        help='''Pass this flag to generate a single expected model for all
        infiles.''')
    expected_parser.set_defaults(func=expected_tool)


def expected_tool(parser, args):
    import os

    from lib5c.tools.helpers import resolve_parallel, resolve_level, \
        resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.plotters.expected import plot_bin_expected, \
        plot_fragment_expected
    from lib5c.algorithms.expected import make_expected_matrix, \
        get_global_distance_expected

    # -S not implemented
    if args.single_model:
        raise NotImplementedError('single model not implemented yet')

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.infile, args.primerfile)
    resolve_parallel(parser, args, subcommand='expected')

    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # resolve level
    resolved_level = resolve_level(primermap, args.level)

    # honor -G
    if args.global_expected:
        distance_expected = get_global_distance_expected(
            counts,
            primermap=primermap,
            level=resolved_level,
            powerlaw=args.powerlaw,
            regression=args.regression,
            degree=args.degree,
            lowess_smooth=args.lowess,
            lowess_frac=args.smoothing_fraction,
            log_transform=args.log_transform,
            exclude_near_diagonal=args.exclude_near_diagonal
        )
    else:
        distance_expected = None

    # make expected
    expected_counts, distance_expected, distance_matrix = make_expected_matrix(
        counts,
        regional_primermap=primermap,
        level=resolved_level,
        powerlaw=args.powerlaw,
        regression=args.regression,
        degree=args.degree,
        lowess_smooth=args.lowess,
        lowess_frac=args.smoothing_fraction,
        log_transform=args.log_transform,
        monotonic=args.force_monotonic,
        donut=args.donut_correction,
        w=args.donut_outer_size,
        p=args.donut_inner_size,
        donut_frac=args.minimum_donut_fraction,
        min_exp=args.min_exp,
        log_donut=args.log_donut,
        max_donut_ll=args.max_with_lower_left,
        distance_expected=distance_expected,
        exclude_near_diagonal=args.exclude_near_diagonal
    )

    # plot outfile
    if args.plot_outfile is not None:
        root_dir = os.path.split(args.outfile)[0]
        outfiles = {region: args.plot_outfile.replace(r'%r', region)
                                             .replace(r'%d', root_dir)
                    for region in counts.keys()}
        if resolved_level == 'bin':
            plot_bin_expected(
                counts,
                distance_expected,
                title={region: '%s 1-D expected model' % region
                       for region in counts.keys()},
                kde=args.kde,
                hexbin=args.hexbin,
                outfile=outfiles
            )
        else:
            plot_fragment_expected(
                counts,
                distance_expected,
                distance_matrix,
                title={region: '%s 1-D expected model' % region
                       for region in counts.keys()},
                kde=args.kde,
                hexbin=args.hexbin,
                outfile=outfiles
            )

    # write counts
    write_counts(expected_counts, args.outfile, primermap)
