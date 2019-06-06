from lib5c.tools.parents import parallelization_parser, \
    region_parser, primerfile_parser


def add_visualize_splines_tool(parser):
    visualize_splines_parser = parser.add_parser(
        'visualize-splines',
        prog='lib5c plot visualize-splines',
        help='visualize splines compared to raw data',
        parents=[primerfile_parser, parallelization_parser, region_parser]
    )
    visualize_splines_parser.add_argument(
        'observed',
        type=str,
        help='''Countsfile containing observed counts to compare to spline.''')
    visualize_splines_parser.add_argument(
        'splines',
        type=str,
        help='''Pickle file containing splines fit by 'lib5c spline'.''')
    visualize_splines_parser.add_argument(
        'bias_factor',
        type=str,
        help='''The bias factor to plot the spline for.''')
    visualize_splines_parser.add_argument(
        '-g', '--grid_points',
        type=int,
        default=10,
        help='''The number of grid points to use for the wireframe
        representation of the spline. The default is 10.''')
    visualize_splines_parser.add_argument(
        '-s', '--sampling_rate',
        type=int,
        default=100,
        help='''Only scatterplot every nth point. The default is 100.''')
    visualize_splines_parser.add_argument(
        '-U', '--unlog',
        action='store_true',
        help='''Pass this flag to fit the splines on unlogged counts. By
        default, they will be fit to logged counts.''')
    visualize_splines_parser.add_argument(
        '-A', '--asymmetric',
        action='store_true',
        help='''Pass this flag to consider only the upper triangular entries of
        the contact matrices.''')
    visualize_splines_parser.set_defaults(func=visualize_splines_tool)


def visualize_splines_tool(parser, args):
    import pickle

    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.plotters.splines import visualize_spline
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.observed, args.primerfile)
    resolve_parallel(parser, args, subcommand='plot visualize-splines',
                     key_arg='observed')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.observed, primermap)

    # load pickle
    with open(args.splines, 'rb') as handle:
        splines = pickle.load(handle)

    # visualize
    print('visualizing')
    visualize_spline([counts], primermap, args.bias_factor,
                     splines[args.bias_factor], grid_points=args.grid_points,
                     sample_rate=args.sampling_rate, log=not args.unlog,
                     asymmetric=args.asymmetric)
