from lib5c.tools.parents import lim_parser, primerfile_parser, var_parser


def add_visualize_variance_tool(parser):
    visualize_variance_parser = parser.add_parser(
        'visualize-variance',
        prog='lib5c plot visualize-variance',
        help='visualize variance estimates',
        parents=[primerfile_parser, lim_parser, var_parser]
    )
    visualize_variance_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts.''')
    visualize_variance_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    visualize_variance_parser.add_argument(
        'outfile',
        type=str,
        help='''Filename to draw plot to.''')
    visualize_variance_parser.add_argument(
        '--x_unit',
        type=str,
        choices=['dist', 'exp'],
        default='dist',
        help='''The x-units of the plot. Default is 'dist'.''')
    visualize_variance_parser.add_argument(
        '--y_unit',
        type=str,
        choices=['disp', 'var'],
        default='var',
        help='''The y-units of the plot. Default is 'var'.''')
    visualize_variance_parser.add_argument(
        '--logx',
        action='store_true',
        help='''Pass to log the x-axis.''')
    visualize_variance_parser.add_argument(
        '--unlogy',
        action='store_true',
        help='''Pass to log the y-axis (default is to log it).''')
    visualize_variance_parser.add_argument(
        '-S', '--scatter',
        action='store_true',
        help='''Pass to plot a simple scatterplot (default is a hexbin
        plot).''')
    visualize_variance_parser.add_argument(
        '-v', '--variance',
        help='''Pass a countsfile of variance estimates to overlay the estimates
        over the data.''')
    visualize_variance_parser.add_argument(
        '-X', '--adjust_x',
        action='store_true',
        help='''If -v/--variance is passed and was estimated with --x_unit exp,
        but is now being visualized with --x_unit dist, pass this flag to use
        the average disp at every dist to make the plotted estimate a function
        of distance. This doesn't work in the other direction (--x_unit of the
        fit was dist but is being visualized as exp).''')
    visualize_variance_parser.add_argument(
        '-Y', '--adjust_y',
        action='store_true',
        help='''If -v/--variance is passed and was estimated with --x_unit dist
        and different --y_unit than it is being visualized with here, and
        --x_unit is dist, pass this flag to use the average exp at each distance
        to make the plotted estimate a function of distance. If variance was
        estimated with --x_unit exp, you can change --y_unit without passing
        this flag.''')
    visualize_variance_parser.add_argument(
        '-r', '--region',
        type=str,
        help='''Pass a region name as a string to visualize the variance for
        only one region.''')
    visualize_variance_parser.set_defaults(func=visualize_variance_tool)


def visualize_variance_tool(parser, args):
    import glob
    import numpy as np
    from lib5c.tools.helpers import resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import flatten_and_filter_counts
    from lib5c.algorithms.variance import estimate_variance
    from lib5c.algorithms.variance.lognorm_dispersion import \
        variance_to_dispersion as lognorm_var_to_disp, \
        dispersion_to_variance as lognorm_disp_to_var, \
        dispersion_to_variance_direct as lognorm_disp_to_var_direct
    from lib5c.algorithms.variance.nbinom_dispersion import \
        variance_to_dispersion as nbinom_var_to_disp, \
        dispersion_to_variance as nbinom_disp_to_var
    from lib5c.algorithms.expected import global_lowess_binned_log_counts
    from lib5c.plotters.scatter import scatter
    from lib5c.plotters.curve_fits import plot_fit

    # resolve primerfile
    primerfile = resolve_primerfile(args.observed, args.primerfile)

    # load expected
    primermap = load_primermap(primerfile)
    expected_counts = load_counts(args.expected, primermap)

    # resolve xlim and ylim
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else None
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # base value for key rep, will be resolved inside the next block
    key_rep = None

    # special loading for cross-replicate mode
    if 'cross_rep' in args.source:
        # expand infiles
        expanded_infiles = glob.glob(args.observed)
        if len(expanded_infiles) < 2:
            raise ValueError('cross-replicate variance estimation requires at '
                             'least 2 replicates')

        # resolve key rep
        if args.rep is not None:
            for expanded_infile in expanded_infiles:
                if args.rep in expanded_infile:
                    key_rep = expanded_infile
                    break

        # load counts
        observed_counts = {
            expanded_infile: load_counts(expanded_infile, primermap)
            for expanded_infile in expanded_infiles}
    else:
        observed_counts = load_counts(args.observed, primermap)

    print('preparing to plot')
    # estimate variance
    variance = estimate_variance(
        observed_counts, expected_counts, key_rep=key_rep, model=args.model,
        source=args.source, fitter='none', min_disp=float(args.min_disp),
        min_obs=args.min_obs, min_dist=args.min_dist,
        regional=args.region is not None)

    # subset region if necessary
    if args.region is not None:
        # no need to subset observed_counts, they aren't used after variance
        # estimation
        expected_counts = {args.region: expected_counts[args.region]}
        variance = {args.region: variance[args.region]}

    # flatten, including var hat if passed
    count_types = {'exp': expected_counts, 'var': variance}
    if args.variance is not None:
        var_hat_counts = load_counts(args.variance, primermap)
        count_types['var_hat'] = {args.region: var_hat_counts[args.region]} \
            if args.region is not None else var_hat_counts
    flat, _, _ = flatten_and_filter_counts(count_types)

    # prepare one-dimensional model if we need it
    exp_model = np.array(global_lowess_binned_log_counts(
        expected_counts, exclude_near_diagonal=True)) \
        if args.adjust_x or args.adjust_y else None

    # decide units for plotting
    x = flat['dist'] if args.x_unit == 'dist' else flat['exp']
    var_to_disp = lognorm_var_to_disp if args.model == 'lognorm' \
        else nbinom_var_to_disp if args.model == 'nbinom' else lambda a, b: a
    disp_to_var = lognorm_disp_to_var if args.model == 'lognorm' \
        else nbinom_disp_to_var if args.model == 'nbinom' else lambda a, b: a
    if args.y_unit == 'disp':
        y = var_to_disp(flat['var'], flat['exp'])
        if args.variance is not None:
            flat['var_hat'] = \
                var_to_disp(flat['var_hat'], exp_model[flat['dist']])\
                if args.adjust_y \
                else var_to_disp(flat['var_hat'], flat['exp'])
            if args.adjust_x:
                for d in np.unique(flat['dist']):
                    flat['var_hat'][flat['dist'] == d] = \
                        np.mean(flat['var_hat'][flat['dist'] == d])
    else:
        y = flat['var']
        if args.model == 'norm':
            disp_to_var = lognorm_disp_to_var_direct
            y = disp_to_var(y, flat['exp'])
        if args.variance is not None:
            if args.adjust_x or args.adjust_y:
                disp_hat = var_to_disp(flat['var_hat'], flat['exp'])
                if args.adjust_x:
                    for d in np.unique(flat['dist']):
                        disp_hat[flat['dist'] == d] = \
                            np.mean(disp_hat[flat['dist'] == d])
                flat['var_hat'] = disp_to_var(
                    disp_hat, exp_model[flat['dist']] if args.adjust_y
                    or (args.adjust_x and args.x_unit == 'dist')
                    else flat['exp'])

    # extra check in case disp_to_var made y infinite
    idx = np.isfinite(y)
    x = x[idx]
    y = y[idx]
    if args.variance is not None:
        flat['var_hat'] = flat['var_hat'][idx]

    print('plotting')
    if args.variance is not None:
        plot_fit(x, y, flat['var_hat'], logx=args.logx, logy=not args.unlogy,
                 hexbin=not args.scatter, xlabel=args.x_unit,
                 ylabel=args.y_unit, xlim=xlim, ylim=ylim, outfile=args.outfile)
    else:
        scatter(x, y, logx=args.logx, logy=not args.unlogy,
                hexbin=not args.scatter, xlabel=args.x_unit,
                ylabel=args.y_unit, xlim=xlim, ylim=ylim, outfile=args.outfile)
