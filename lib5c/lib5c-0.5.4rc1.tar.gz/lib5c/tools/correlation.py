import argparse
from lib5c.tools.parents import primerfile_parser


def add_correlation_tool(parser):
    correlation_parser = parser.add_parser(
        'correlation',
        prog='lib5c plot correlation',
        help='compute pairwise correlation coefficients',
        parents=[primerfile_parser]
    )
    correlation_parser.add_argument(
        '-P', '--pearson',
        action='store_true',
        help='''Compute Pearson correlation coefficients.''')
    correlation_parser.add_argument(
        '-S', '--spearman',
        action='store_true',
        help='''Compute Spearman correlation coefficients.''')
    # correlation_parser.add_argument(
    #    '-r', '--region',
    #    type=str,
    #    help='''If passed, compute correlations only for the specified
    #    region.''')
    correlation_parser.add_argument(
        '-c', '--csv',
        type=str,
        help='''Specify an output file to write output as csv. %%c will be
        replaced with the correlation type.''')
    correlation_parser.add_argument(
        '-i', '--image',
        type=str,
        help='''Specify an output file to write output as image. %%c will be
        replaced with the correlation type.''')
    correlation_parser.add_argument(
        '-s', '--scale',
        type=str,
        default=None,
        help='''Specify a colorscale to use when writing output image by passing
        a string of the form '(min, max)'.''')
    correlation_parser.add_argument(
        '-B', '--colorbar',
        action='store_true',
        help='''Add a colorbar to the plot. Ignored when -C/--cluster is
        passed.''')
    correlation_parser.add_argument(
        '-C', '--cluster',
        action='store_true',
        help='''Cluster the samples when writing output image.''')
    correlation_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to compute correlations between.''')
    correlation_parser.set_defaults(func=correlation_tool)


def correlation_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, infer_replicate_names
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.algorithms.correlation import make_pairwise_correlation_matrix
    from lib5c.plotters.correlation import plot_correlation_matrix
    from lib5c.writers.correlation import write_correlation_table
    from lib5c.util.system import check_outdir

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # resolve colorscale
    colorscale = map(float, args.scale.strip('()').split(',')) \
        if args.scale is not None else None

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts_superdict = {expanded_infile: load_counts(expanded_infile, primermap)
                        for expanded_infile in expanded_infiles}

    # build correlation type list
    correlation_types = []
    if args.pearson:
        correlation_types.append('pearson')
    if args.spearman:
        correlation_types.append('spearman')

    # sort and prettify filenames for use as labels
    rep_order = sorted(expanded_infiles)
    labels = infer_replicate_names(
        rep_order, pattern=args.countsfiles[0] if len(args.countsfiles) == 1
        and '*' in args.countsfiles[0] else None)

    # make matrices and write output
    for correlation_type in correlation_types:

        correlation_matrix = make_pairwise_correlation_matrix(
            counts_superdict, correlation=correlation_type, rep_order=rep_order)

        if args.image is not None:
            outfile = args.image.replace('%c', correlation_type)
            plot_correlation_matrix(
                correlation_matrix, label_values=labels, cluster=args.cluster,
                cbar=args.colorbar, colorscale=colorscale, outfile=outfile)

        if args.csv is not None:
            outfile = args.csv.replace('%c', correlation_type)
            check_outdir(outfile)
            write_correlation_table(correlation_matrix, outfile, labels=labels)

        print '%s correlation matrix:' % correlation_type
        print correlation_matrix
        print ''
