import argparse

from lib5c.tools.parents import lim_parser, primerfile_parser


def add_distribution_tool(parser):
    distribution_parser = parser.add_parser(
        'distribution',
        prog='lib5c plot distribution',
        help='plot distributions',
        parents=[primerfile_parser, lim_parser]
    )
    distribution_parser.add_argument(
        '-r', '--region',
        type=str,
        help='''Pass this flag to plot distributions for a specific region.''')
    distribution_parser.add_argument(
        '-R', '--regional',
        action='store_true',
        help='''Pass this flag to plot distributions for all regions separately.
        %%r in the output filename will be''')
    distribution_parser.add_argument(
        '-Z', '--drop_zeros',
        action='store_true',
        help='''Pass this flag to plot only the positive part of the
        distribution.''')
    distribution_parser.add_argument(
        '-s', '--separate_colors',
        type=str,
        help='''Specify a shell-quoted, comma-separated list of class names
        (which must be substrings of the replicate names) to color-code the
        output with. For example, 'ES,NPC'.''')
    distribution_parser.add_argument(
        'outfile',
        type=str,
        help='''Filename to draw plot to.''')
    distribution_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to plot distributions for.''')
    distribution_parser.set_defaults(func=distribtion_tool)


def distribtion_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, \
        infer_replicate_names, infer_level_mapping
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.plotters.distribution import plot_regional_distribtions, \
        plot_global_distributions, plot_regional_distribtions_parallel

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # resolve xlim and ylim
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else None
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts_superdict = {expanded_infile: load_counts(expanded_infile, primermap)
                        for expanded_infile in expanded_infiles}

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
    if args.region is not None:
        plot_regional_distribtions(
            {infile: counts_superdict[infile][args.region]
             for infile in expanded_infiles},
            labels=rep_names,
            levels=levels,
            outfile=args.outfile,
            xlim=xlim,
            ylim=ylim
        )
    elif args.regional:
        outfiles = {region: args.outfile.replace(r'%r', region)
                    for region in primermap.keys()}
        plot_regional_distribtions_parallel(
            {region: {infile: counts_superdict[infile][region]
                      for infile in expanded_infiles}
             for region in primermap.keys()},
            labels=rep_names,
            levels=levels,
            outfile=outfiles,
            xlim=xlim,
            ylim=ylim
        )
    else:
        plot_global_distributions(
            counts_superdict,
            labels=rep_names,
            levels=levels,
            outfile=args.outfile,
            xlim=xlim,
            ylim=ylim
        )
