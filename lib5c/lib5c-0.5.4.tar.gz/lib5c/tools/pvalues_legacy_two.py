from lib5c.tools.parents import level_parser, parallelization_parser, \
    primerfile_parser


def add_pvalues_tool(parser):
    pvalues_parser = parser.add_parser(
        'pvalues2',
        help='new experimental pvalue caller',
        parents=[primerfile_parser, level_parser, parallelization_parser]
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
        'outfile',
        type=str,
        help='''Path to file to write p-values to.''')
    pvalues_parser.add_argument(
        '-g', '--group_by',
        type=str,
        choices=['expected', 'distance', 'donut'],
        default='expected',
        help='''Specify how interactions should be grouped. Default is
        'expected'.''')
    pvalues_parser.add_argument(
        '-f', '--fractional_tolerance',
        type=float,
        default=0.1,
        help='''When grouping by expected, specify how wide the ranges of
        expected values should be in each group. Default is 0.1.''')
    pvalues_parser.add_argument(
        '-t', '--distance_tolerance',
        type=int,
        default=2,
        help='''When grouping by distance, specify how wide the ranges of
        distances should be within each group in bin units. Default is 2.''')
    pvalues_parser.add_argument(
        '-w', '--donut_outer_size',
        type=int,
        default=15,
        help='''When grouping by donut, the outer size of the donut to use. The
        default is 15.''')
    pvalues_parser.add_argument(
        '-x', '--donut_inner_size',
        type=int,
        default=5,
        help='''When grouping by donut, the inner size of the donut to use. The
        default is 5.''')
    pvalues_parser.add_argument(
        '-d', '--distribution',
        type=str,
        default='nbinom',
        help='''The distribution to use to evaluate the p-values. This must be a
        subclass of scipy.stats.rv_discrete or scipy.stats.rv_continuous. If it
        is a subclass of rv_discrete, approaches that depend on MLE fits may be
        unavailable. The default is 'nbinom'.''')
    pvalues_parser.add_argument(
        '-L', '--log',
        action='store_true',
        help='''Pass this flag to treat the distribution specified by the
        -d/--distribution flag as modeling the counts in log space.''')
    pvalues_parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['log_log_fit', 'obs_over_exp', 'mle'],
        default='obs_over_exp',
        help='''Specify what mode to use to estimate the variance. 'log_log_fit'
        fits a quadratic mean-variance relationship according to the grouping.
        'obs_over_exp' uses the sample variance of the observed over the
        expected values to infer a quadratic mean-variance relationship,
        ignoring the grouping. 'mle' fits a distribution to each group in the
        grouping. The default is 'obs_over_exp'.''')
    pvalues_parser.add_argument(
        '-b', '--bias_vector',
        type=str,
        help='''File containing a bias vector. If this flag is present, the
        p-value computation will be performed in deconvoluted space.''')
    pvalues_parser.add_argument(
        '-o', '--plot_outfile',
        type=str,
        default='mvr_%r.png',
        help='''Pattern to write diagnostic plots to.''')
    pvalues_parser.set_defaults(func=pvalues_tool)


def pvalues_tool(parser, args):
    import scipy.stats as stats

    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.bias import load_bias_vector
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.algorithms.variance_legacy.grouping import\
        group_by_bin_distance_parallel, group_by_expected_value_parallel
    from lib5c.algorithms.variance_legacy.mle import \
        make_moment_matrices_parallel, donut_moment_estimate_parallel
    from lib5c.algorithms.variance_legacy.mvr.log_log import \
        learn_mvr_parallel as learn_log_log_mvr, \
        learn_mvr_from_matrices_parallel
    from lib5c.algorithms.variance_legacy.mvr.obs_over_exp_sample_variance \
        import learn_mvr_parallel as learn_obs_over_exp_mvr
    from lib5c.algorithms.variance_legacy.mvr.apply_mvr import \
        apply_mvr_parallel
    from lib5c.algorithms.variance_legacy.pvalues import call_pvalues_parallel

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='pvalues2', key_arg='observed')
    primerfile = resolve_primerfile(args.observed, args.primerfile)

    # resolve dist_gen
    dist_gen = getattr(stats, args.distribution)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)

    # load bias vector
    if args.bias_vector is not None:
        print('loading bias vector')
        bias = load_bias_vector(args.bias_vector, primermap)
    else:
        bias = {region: None for region in observed_counts.keys()}

    # donut has its own logic
    if args.group_by == 'donut':
        print('grouping by donut')
        if args.mode == 'mle':
            expected_counts = donut_moment_estimate_parallel(
                observed_counts, dist_gen, moment=1, p=args.donut_inner_size,
                w=args.donut_outer_size, log=args.log)
            variance_counts = donut_moment_estimate_parallel(
                observed_counts, dist_gen, moment=2, p=args.donut_inner_size,
                w=args.donut_outer_size, log=args.log)
        elif args.mode == 'log_log_fit':
            if args.log:
                raise NotImplementedError('log-log fit mode not implemented '
                                          'for log-scale distributions')
            donut_expected_counts = donut_moment_estimate_parallel(
                observed_counts, stats.norm, moment=1, p=args.donut_inner_size,
                w=args.donut_outer_size)
            donut_variance_counts = donut_moment_estimate_parallel(
                observed_counts, stats.norm, moment=2, p=args.donut_inner_size,
                w=args.donut_outer_size)
            mvr = learn_mvr_from_matrices_parallel(
                donut_expected_counts,
                donut_variance_counts,
                plot_outfile={region: args.plot_outfile.replace('%r', region)
                              for region in primermap.keys()}
            )
            expected_counts, variance_counts = apply_mvr_parallel(
                expected_counts, mvr)
        else:
            raise NotImplementedError(
                'donut grouping not implemented in obs_over_exp mode')
    else:
        # group points
        if args.mode == 'obs_over_exp':
            print('skipping grouping')
            groups = None
        else:
            print('grouping by %s' % args.group_by)
            if args.group_by == 'distance':
                groups = group_by_bin_distance_parallel(
                    observed_counts, args.distance_tolerance)
            elif args.group_by == 'expected':
                groups = group_by_expected_value_parallel(
                    observed_counts, expected_counts, args.fractional_tolerance)
            else:
                raise ValueError('invalid grouping strategy')

        # get variance
        print('estimating variance')
        if args.mode == 'mle':
            expected_counts, variance_counts = make_moment_matrices_parallel(
                groups, dist_gen, log=args.log)
        elif args.mode == 'log_log_fit':
            if args.log:
                raise NotImplementedError('log-log fit mode not implemented '
                                          'for log-scale distributions')
            mvr = learn_log_log_mvr(
                groups,
                plot_outfile={region: args.plot_outfile.replace('%r', region)
                              for region in primermap.keys()}
            )
            expected_counts, variance_counts = apply_mvr_parallel(
                expected_counts, mvr)
        elif args.mode == 'obs_over_exp':
            mvr = learn_obs_over_exp_mvr(
                observed_counts, expected_counts, log=args.log)
            expected_counts, variance_counts = apply_mvr_parallel(
                expected_counts, mvr)
        else:
            raise ValueError('invalid variance strategy')

    # compute pvalues
    print('computing pvalues')
    pvalues = call_pvalues_parallel(
        observed_counts, expected_counts, variance_counts, dist_gen,
        log=args.log, pseudocount=1.0, bias=bias)

    # write p-values
    print('writing p-values')
    write_counts(pvalues, args.outfile, primermap)
