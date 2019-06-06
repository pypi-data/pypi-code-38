from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, primerfile_parser


def add_outliers_tool(parser):
    outliers_parser = parser.add_parser(
        'outliers',
        prog='lib5c outliers',
        help='remove high spatial outliers',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    outliers_parser.add_argument(
        '-f', '--fold_threshold',
        type=float,
        default=8.0,
        help='''Remove any interaction whose fold change relative to the median
        of its local neighborhood would be greater than this value after
        balancing. The default is 8.0.''')
    outliers_parser.add_argument(
        '-w', '--window_size',
        type=int,
        default=5,
        help='''The size of the window to use to define the local neighborhood.
        This value should be an odd integer. The default is 5.''')
    outliers_parser.add_argument(
        '-o', '--overwrite_value',
        type=str,
        choices=['nan', 'median', 'zero'],
        default='nan',
        help='''This flag specifies what value will be used to overwrite the
        high outliers. The default is 'nan'.''')
    outliers_parser.set_defaults(func=outliers_tool)


def outliers_tool(parser, args):
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.tools.helpers import resolve_parallel, resolve_level, \
        resolve_primerfile
    from lib5c.algorithms.outliers import remove_high_spatial_outliers

    # resolve primerfile and parallel
    resolve_parallel(parser, args, subcommand='outliers')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # remove outliers
    processed_counts = remove_high_spatial_outliers(
        counts, size=args.window_size, fold_threshold=args.fold_threshold,
        overwrite_value=args.overwrite_value, primermap=primermap,
        level=resolve_level(primermap, args.level))

    # write counts
    write_counts(processed_counts, args.outfile, primermap)
