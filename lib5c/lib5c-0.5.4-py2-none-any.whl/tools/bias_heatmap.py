from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, primerfile_parser


def add_bias_heatmap_tool(parser):
    bias_heatmap_parser = parser.add_parser(
        'bias-heatmap',
        prog='lib5c plot bias-heatmap',
        help='plot bias heatmap',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    bias_heatmap_parser.add_argument(
        'bias_factor',
        type=str,
        help='''Specify which bias factor to plot heatmaps for. The bias factor
        must match the header label of a column in the primer bedfile, or it
        must be a reference to a bed file containing bias information.''')
    bias_heatmap_parser.add_argument(
        '-D', '--divide_by_length',
        action='store_true',
        help='''If bias_factor is a bed file, divide the number of intersections
        by the length of the fragment in kb.''')
    bias_heatmap_parser.add_argument(
        '-U', '--unlog',
        action='store_true',
        help='''Show the bias on an unlogged fold change scale. By default it
        will be shown on a log2 fold change scale.''')
    bias_heatmap_parser.add_argument(
        '-A', '--asymmetric',
        action='store_true',
        help='''Pass this flag to allow the heatmap to be asymmetric by only
        considering the upper triangular entries of the contact matrices. By
        default, the heatmaps will be symmetric.''')
    bias_heatmap_parser.add_argument(
        '-n', '--num_bins',
        type=int,
        help='''Stratify the bias factor into this many bins with equal numbers
        of loci in each bin.''')
    bias_heatmap_parser.add_argument(
        '-b', '--bins',
        type=str,
        help='''Stratify the bias factor into bins based on these boundaries,
        which should be passed as a comma-separated list such as
        '(min,split1,split2,max)'.''')
    bias_heatmap_parser.add_argument(
        '-c', '--colormap',
        type=str,
        default='bias',
        help='''Specify the colormap to use. Special values include 'bias'. The
        default is 'bias'.''')
    bias_heatmap_parser.add_argument(
        '-s', '--scale',
        type=str,
        default='(-1.0,1.0)',
        help='''Specify the scale for the heatmap colorbar. The default is
        '(-1.0,1.0)'.''')
    bias_heatmap_parser.add_argument(
        '-m', '--midpoint',
        type=float,
        default=0.5,
        help='''Force a midpoint for the colormap, as a fraction of the range of
        the scale. The default is 0.5.''')
    bias_heatmap_parser.add_argument(
        '-r', '--region',
        type=str,
        help='''Only include counts from this region.''')
    bias_heatmap_parser.add_argument(
        '-e', '--expected_model',
        type=str,
        help='''Pass a string reference to a countsfile containing the expected
        model to be used. If this is not passed, a linear log-log fit will be
        used.''')
    bias_heatmap_parser.add_argument(
        '-Z', '--zero_inflated',
        action='store_true',
        help='''Pass this flag to treat the bias factor as "zero inflated",
        which will cause all the zero values to land in a dedicated "zero
        stratum" and allocate the remaining bins evenly among the positive
        data.''')
    bias_heatmap_parser.add_argument(
        '-Q', '--unique',
        action='store_true',
        help='''Pass this flag to ignore -b/--bins and -n/--num_bins and instead
        group each unique value of the bias factor into its own stratum.''')
    bias_heatmap_parser.set_defaults(func=bias_heatmap_tool)


def bias_heatmap_tool(parser, args):
    import os

    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile, \
        resolve_level
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.parsers.bed import load_features
    from lib5c.util.bed import count_intersections
    from lib5c.plotters.colormaps import get_colormap
    from lib5c.plotters.bias_heatmaps import plot_bias_heatmap
    from lib5c.algorithms.expected import \
        make_poly_log_log_binned_expected_matrix, \
        make_poly_log_log_fragment_expected_matrix

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='plot bias-heatmap')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    obs_counts = load_counts(args.infile, primermap)
    if args.expected_model:
        exp_counts = load_counts(args.expected_model, primermap)
    else:
        if resolve_level(primermap, args.level) == 'fragment':
            exp_counts = make_poly_log_log_fragment_expected_matrix(
                obs_counts, primermap)
        else:
            exp_counts = make_poly_log_log_binned_expected_matrix(obs_counts)

    print('preparing to plot')
    # parse vmin and vmax from args.scale
    vmin, vmax = map(float, args.scale.strip('()').split(','))

    # parse bins if passed
    bins = map(float, args.bins.strip('()').split(',')) \
        if args.bins is not None else None

    # resolve colormap
    cmap = get_colormap(args.colormap)

    # resolve log
    log = True
    if args.unlog:
        log = False

    # resolve bias_factor
    if os.path.exists(args.bias_factor):
        boundaries = [{'start': primermap[region][0]['start'],
                       'end'  : primermap[region][-1]['end'],
                       'chrom': primermap[region][0]['chrom']}
                      for region in primermap.keys()]
        features = load_features(args.bias_factor, boundaries=boundaries)
        for region in primermap.keys():
            for i in range(len(primermap[region])):
                primermap[region][i]['peaks'] = count_intersections(
                    primermap[region][i],
                    features[primermap[region][i]['chrom']])
                primermap[region][i]['peaks per kb'] = \
                    primermap[region][i]['peaks'] * 1000 / \
                    float(primermap[region][i]['length'])
        if args.divide_by_length:
            resolved_bias_factor = 'peaks per kb'
        else:
            resolved_bias_factor = 'peaks'
    else:
        resolved_bias_factor = args.bias_factor

    # plot heatmap
    print('plotting')
    plot_bias_heatmap(
        obs_counts, exp_counts, primermap, resolved_bias_factor,
        bins=bins, n_bins=args.num_bins, cmap=cmap, vmin=vmin, vmax=vmax,
        midpoint=args.midpoint, log=log, region=args.region,
        asymmetric=args.asymmetric, zero_inflated=args.zero_inflated,
        unique=args.unique, outfile=args.outfile)
