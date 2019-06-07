from lib5c.tools.parents import primerfile_parser, lim_parser


def add_convergency_tool(parser):
    convergency_parser = parser.add_parser(
        'convergency',
        prog='lib5c plot convergency',
        help='compute transcription factor convergency',
        parents=[primerfile_parser, lim_parser]
    )
    convergency_parser.add_argument(
        '-i', '--image',
        type=str,
        help='''Specify an output file to write output as image.''')
    convergency_parser.add_argument(
        '-s', '--strand_column',
        type=int,
        default=5,
        help='''The 0-based index of the column in the motiffile which contains
        the strand information (+/-). Default is 5.''')
    convergency_parser.add_argument(
        '-m', '--margin',
        type=int,
        default=0,
        help='''The margin for error (in bin units) with which to judge the
        intersections. Default is 0.''')
    convergency_parser.add_argument(
        '-l', '--loop_classes',
        type=str,
        default='constitutive',
        help='''The loop classes to consider, passed as a shell-quoted,
        comma-separated list. Default is 'constitutive'.''')
    convergency_parser.add_argument(
        'motiffile',
        type=str,
        help='''Bedfile describing motifs.''')
    convergency_parser.add_argument(
        'peakfile',
        type=str,
        help='''Bedfile describing occupied peaks.''')
    convergency_parser.add_argument(
        'countsfile',
        type=str,
        help='''Countsfiles of loop classes.''')
    convergency_parser.set_defaults(func=convergency_tool)


def convergency_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.parsers.bed import load_features
    from lib5c.algorithms.convergency import compute_convergency
    from lib5c.plotters.convergency import plot_convergency

    # resolve plot_kwargs
    xlim = map(float, args.xlim.strip('()').split(',')) \
        if args.xlim is not None else None
    ylim = map(float, args.ylim.strip('()').split(',')) \
        if args.ylim is not None else None

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfile, args.primerfile)

    # resolve loop classes
    loop_classes = map(str.strip, args.loop_classes.strip('()').split(','))

    # parse things
    peaks = load_features(args.peakfile)
    motifs = load_features(args.motiffile, id_index=args.strand_column)
    primermap = load_primermap(primerfile)
    loops = load_counts(args.countsfile, primermap)

    # compute convergency
    convergency_results = compute_convergency(
        loops, primermap, peaks, motifs, loop_classes=loop_classes,
        margin=args.margin)

    # print to console
    for k in sorted(convergency_results.keys()):
        print '%s: %s (%s)' % (k, convergency_results[k]['foldchange'],
                               convergency_results[k]['pvalue'])

    # plot bargraph
    if args.image is not None:
        plot_convergency(convergency_results, xlim=xlim, ylim=ylim,
                         outfile=args.image)
