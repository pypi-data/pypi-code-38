import argparse

from lib5c.tools.parents import primerfile_parser


def add_dd_curve_tool(parser):
    dd_curve_parser = parser.add_parser(
        'dd-curve',
        prog='lib5c plot dd-curve',
        help='plot distance dependence curve',
        parents=[primerfile_parser]
    )
    dd_curve_parser.add_argument(
        '-r', '--region',
        type=str,
        help='''Pass this flag to plot distributions for a specific region.''')
    dd_curve_parser.add_argument(
        '-R', '--regional',
        action='store_true',
        help='''Pass this flag to plot distributions for all regions separately.
        %%r in the output filename will be''')
    dd_curve_parser.add_argument(
        '-b', '--bins',
        type=str,
        help='''Pass a comma separated list of bin edges to override the default
        distance stratification.'''
    )
    dd_curve_parser.add_argument(
        '-y', '--ylim',
        type=str,
        help='''Pass a tuple '(min,max)' to force the y-limits of the plot.'''
    )
    dd_curve_parser.add_argument(
        '-s', '--separate_colors',
        type=str,
        help='''Specify a shell-quoted, comma-separated list of class names
        (which must be substrings of the replicate names) to color-code the
        output with. For example, 'ES,NPC'.''')
    dd_curve_parser.add_argument(
        'outfile',
        type=str,
        help='''Filename to draw plot to.''')
    dd_curve_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to plot distance dependence curves for.''')
    dd_curve_parser.set_defaults(func=dd_curve_tool)


def dd_curve_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, infer_replicate_names, \
        infer_level_mapping
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.distance_dependence import plot_distance_dependence,\
        plot_distance_dependence_parallel

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # resolve ylim
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # resolve bins
    bins = map(float, args.bins.strip('()').split(',')) \
        if args.bins is not None else None

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts_superdict = {expanded_infile: load_counts(expanded_infile, primermap)
                        for expanded_infile in expanded_infiles}

    # establish reps and regions
    reps = counts_superdict.keys()
    regions = primermap.keys()

    # compute labels
    rep_names = infer_replicate_names(
        expanded_infiles, as_dict=True, pattern=args.countsfiles[0]
        if len(args.countsfiles) == 1 and '*' in args.countsfiles[0] else None)

    # determine levels
    levels = None
    if args.separate_colors is not None:
        levels = infer_level_mapping(
            rep_names.values(), map(str.strip, args.separate_colors.split(',')))

    # plot
    if args.region or not args.regional:
        plot_distance_dependence(
            counts_superdict,
            primermap,
            region=args.region,
            bins=bins,
            labels=rep_names,
            levels=levels,
            outfile=args.outfile,
            ylim=ylim
        )
    else:
        plot_distance_dependence_parallel(
            {r: {rep: {r: counts_superdict[rep][r]} for rep in reps}
             for r in regions},
            {r: {r: primermap[r]} for r in regions},
            region={r: r for r in regions},
            bins=bins,
            labels=rep_names,
            levels=levels,
            outfile={r: args.outfile.replace(r'%r', r) for r in regions},
            ylim=ylim
        )
