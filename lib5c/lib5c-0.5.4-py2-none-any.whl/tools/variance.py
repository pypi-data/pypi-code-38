from lib5c.tools.parents import parallelization_parser, primerfile_parser, \
    var_parser


def add_variance_tool(parser):
    variance_parser = parser.add_parser(
        'variance',
        prog='lib5c variance',
        help='estimate variances from obs values and exp models',
        parents=[primerfile_parser, parallelization_parser, var_parser]
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
        '--x_unit',
        type=str,
        choices=['exp', 'dist'],
        default='dist',
        help='''X-unit of the variance relationship. Default is 'dist'.''')
    variance_parser.add_argument(
        '--y_unit',
        type=str,
        choices=['disp', 'var'],
        default='disp',
        help='''Y-unit of the variance relationship. Default is 'disp'.''')
    variance_parser.add_argument(
        '--logx',
        action='store_true',
        help='''Pass this flag to perform the variance relationship fitting on
        the scale of log(x).''')
    variance_parser.add_argument(
        '--logy',
        action='store_true',
        help='''Pass this flag to perform the variance relationship fitting on
        the scale of log(y).''')
    variance_parser.add_argument(
        '-R', '--regional',
        action='store_true',
        help='''Pass this to perform a separate variance estimation step for
        each region.''')
    variance_parser.set_defaults(func=variance_tool)


def variance_tool(parser, args):
    import glob
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.algorithms.variance import estimate_variance
    from lib5c.writers.counts import write_counts

    # resolve primerfile
    primerfile = resolve_primerfile(args.observed, args.primerfile)

    # short-circuit to cross-replicate mode
    if 'cross_rep' in args.source:
        # expand infiles
        expanded_infiles = glob.glob(args.observed)
        if len(expanded_infiles) < 2:
            raise ValueError('cross-replicate variance estimation requires at '
                             'least 2 replicates')

        # resolve key rep
        key_rep = None
        if args.rep is not None:
            for expanded_infile in expanded_infiles:
                if args.rep in expanded_infile:
                    key_rep = expanded_infile
                    break

        # load counts
        print('loading counts')
        primermap = load_primermap(primerfile)
        counts_superdict = {
            expanded_infile: load_counts(expanded_infile, primermap)
            for expanded_infile in expanded_infiles}
        expected_counts = load_counts(args.expected, primermap)

        # estimate variance
        print('estimating variance')
        variance = estimate_variance(
            counts_superdict, expected_counts, key_rep=key_rep,
            model=args.model, source=args.source, fitter=args.fitter,
            fitter_agg=args.agg_fn, x_unit=args.x_unit, y_unit=args.y_unit,
            logx=args.logx, logy=args.logy, min_disp=float(args.min_disp),
            min_obs=args.min_obs, min_dist=args.min_dist,
            regional=args.regional)

        # write variance
        print('writing variance')
        write_counts(variance, args.outfile, primermap)

        return

    # resolve parallel
    resolve_parallel(parser, args, subcommand='variance', key_arg='observed')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)

    # estimate variance
    variance = estimate_variance(
        observed_counts, expected_counts, model=args.model,
        source=args.source, fitter=args.fitter, fitter_agg=args.agg_fn,
        x_unit=args.x_unit, y_unit=args.y_unit, logx=args.logx, logy=args.logy,
        min_disp=float(args.min_disp), min_obs=args.min_obs,
        min_dist=args.min_dist, regional=args.regional)

    # write variance
    print('writing variance')
    write_counts(variance, args.outfile, primermap)
