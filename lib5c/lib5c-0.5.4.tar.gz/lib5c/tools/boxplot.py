from lib5c.tools.parents import simple_in_out_parser, parallelization_parser, \
    region_parser, primerfile_parser


def add_boxplot_tool(parser):
    boxplot_parser = parser.add_parser(
        'boxplot',
        prog='lib5c plot boxplot',
        help='plot boxplot of counts at each locus',
        parents=[primerfile_parser, simple_in_out_parser, region_parser,
                 parallelization_parser]
    )
    boxplot_parser.add_argument(
        '-S', '--sorted', action='store_true', help='''Sort the loci by
        median.''')
    boxplot_parser.add_argument(
        '-L', '--logged', action='store_true', help='''Log counts before drawing
        the boxplots.''')
    boxplot_parser.add_argument(
        '-y', '--y_limits', type=str, help='''Set the y-limits of the boxplots
        manually by passing a string of the form '(min, max)'.''')
    boxplot_parser.add_argument(
        '-c', '--color', type=str, default='darkgray', help='''Set the color of
        the boxes. The default is 'darkgray'.''')
    boxplot_parser.add_argument(
        '-m', '--median_color', type=str, default='firebrick', help='''Set the
        color of the medians. The default is 'firebrick'.''')
    boxplot_parser.add_argument(
        '-w', '--median_linewidth', type=float, default=5.0, help='''Set the
        thickness of the medians. The default is 5.0''')
    boxplot_parser.add_argument(
        '-d', '--dpi', type=int, default=300, help='''Specify the DPI at which
        to draw the figure. The default is 300.''')
    boxplot_parser.add_argument(
        '-s', '--scaling_factor', type=float, default=0.05, help='''Specify a
        scaling factor to use to automatically determine the figure size. The
        default is 0.05''')
    boxplot_parser.add_argument(
        '-f', '--figure_size', type=str, help='''Specify the size of the figure
        in inches as a string literal of the form '(width, height)'.''')
    boxplot_parser.set_defaults(func=boxplot_tool)


def boxplot_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.boxplots import plot_regional_locus_boxplot

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='plot boxplot')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    print('preparing to plot')
    # resolve region
    if args.region is not None:
        counts = counts[args.region]

    # resolve outfile
    if args.region:
        resolved_outfile = args.outfile
    else:
        resolved_outfile = {region: args.outfile.replace(r'%r', region)
                            for region in counts.keys()}

    # resolve figure_size
    figsize = map(float, args.figure_size.strip('()').split(',')) \
        if args.figure_size else None

    # resolve y_limits
    ylim = map(float, args.y_limits.strip('()').split(',')) \
        if args.y_limits else None

    # plot boxplot
    print('plotting')
    plot_regional_locus_boxplot(
        counts, color=args.color, median_color=args.median_color,
        median_linewidth=args.median_linewidth, logged=args.logged,
        sort=args.sorted, figsize=figsize, scaling_factor=args.scaling_factor,
        ylim=ylim, dpi=args.dpi, outfile=resolved_outfile)
