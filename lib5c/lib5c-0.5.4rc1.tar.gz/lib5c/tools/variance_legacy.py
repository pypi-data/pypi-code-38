from lib5c.tools.parents import parallelization_parser, \
    donut_parser, expected_selection_parser, primerfile_parser


def add_variance_tool(parser):
    variance_parser = parser.add_parser(
        'variance',
        prog='lib5c variance',
        help='estimate variances from obs values and exp models',
        description='note: if none of -D/-P/-V/-R/-G are passed, the variance '
                    'will be estimated using a per-region MLE fit of the '
                    'negative binomial dispersion parameter across all pixels '
                    'in the region',
        parents=[primerfile_parser, parallelization_parser, donut_parser,
                 expected_selection_parser]
    )
    variance_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts.''')
    variance_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    variance_parser.add_argument(
        'outfile',
        type=str,
        help='''Path to file to write variance counts to.''')
    variance_parser.add_argument(
        '-P', '--poisson',
        action='store_true',
        help='''Pass this flag to skip variance estimation and instead simply
        copy the expected counts to the outfile. Overrides -V/-D, ignores
        -n/-f and -v/-w.''')
    variance_parser.add_argument(
        '-V', '--vst',
        action='store_true',
        help='''Pass this flag to apply a variance stabilizing transform
        (namely a log transform) before estimating the variance. Can be combined
        with -D to estimate a local stabilized variance estimate at every point.
        If not combined with -D, this ignores -v/-w and estimates the variance
        for each region together as one big group. Always ignores -n/-f''')
    variance_parser.add_argument(
        '-R', '--regional_mvr',
        action='store_true',
        help='''Fit a separate quadratic mean-variance relationship for each
        region. Use -n/-f to control the grouping of points used to fit the MVR.
        Ignored if any of -P/-D/-V is passed. Ignores -v/-w.''')
    variance_parser.add_argument(
        '-G', '--global_mvr',
        action='store_true',
        help='''Fit a single quadratic mean-variance relationship across all
        regions. Use -n/-f to control the grouping of points used to fit the
        MVR. Ignored if any of -P/-D/-V/-R is passed. Ignores -v/-w.''')
    variance_parser.set_defaults(func=variance_tool)


def variance_tool(parser, args):
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.algorithms.variance_legacy.variance import estimate_variance, \
        estimate_global_mvr_variance
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.observed, args.primerfile)
    resolve_parallel(parser, args, subcommand='variance', key_arg='observed')

    # prepare method argument and kwargs dict
    if args.poisson:
        method = 'poisson'
        kwargs = {}
    elif args.donut:
        if args.vst:
            method = 'local_vst'
        else:
            method = 'local'
        kwargs = {'p': args.donut_inner_size, 'w': args.donut_outer_size}
    elif args.vst:
        method = 'vst'
        kwargs = {}
    elif args.regional_mvr:
        method = 'mvr'
        kwargs = {'num_groups': args.num_groups,
                  'group_fractional_tolerance': args.group_fractional_tolerance,
                  'exclude_offdiagonals': args.exclude_offdiagonals}
    elif args.global_mvr:
        method = 'global_mvr'
        kwargs = {'num_groups': args.num_groups,
                  'group_fractional_tolerance': args.group_fractional_tolerance,
                  'exclude_offdiagonals': args.exclude_offdiagonals}
    else:
        method = 'disp'
        kwargs = {}

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)

    # fit distributions
    print('estimating variance')
    if method == 'global_mvr':
        variance = estimate_global_mvr_variance(
            observed_counts, expected_counts, **kwargs)
    else:
        variance = estimate_variance(observed_counts, expected_counts, method,
                                     **kwargs)

    # write variance
    print('writing variance')
    write_counts(variance, args.outfile, primermap)
