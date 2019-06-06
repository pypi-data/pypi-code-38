from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, region_parser, primerfile_parser


def add_heatmap_tool(parser):
    heatmap_parser = parser.add_parser(
        'heatmap',
        prog='lib5c plot heatmap',
        help='plot interaction frequency heatmaps',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 region_parser, parallelization_parser]
    )
    heatmap_parser.add_argument(
        '-c', '--colormap',
        type=str,
        default='obs',
        help='''Specify the colormap to use. Special values include 'obs',
        'abs_obs', 'is', 'obs_over_exp', and 'pvalue'. The default is 'obs'.''')
    heatmap_parser.add_argument(
        '-s', '--scale',
        type=str,
        help='''Specify the colorscale as a string literal of the form
        '(min,max)'. You can write formulas which include the special symbols
        'min', 'max', 'mu' (mean), 'sigma' (standard deviation),
        'p95' (95th percentile), or 'p98' (98th percentile), such as
        '(mu-2.5*sigma,mu+2.5*sigma)'. Alternatively, pass a path to a
        colorscale file as produced by `lib5c colorscale`. Pass nothing to
        visualize the heatmap on a percentile rank scale.''')
    heatmap_parser.add_argument(
        '-g', '--genes',
        type=str,
        help='''If plotting a bin-level heatmap, pass one of 'mm9', 'mm10',
        'hg18', 'hg19', or 'hg38' to add gene tracks for the selected reference
        genome.''')
    heatmap_parser.add_argument(
        '-C', '--colorbar',
        action='store_true',
        help='''Include a colorbar next to the heatmap.''')
    heatmap_parser.add_argument(
        '-R', '--rulers',
        action='store_true',
        help='''Include genomic coordinate rulers on the heatmap.''')
    heatmap_parser.add_argument(
        '-P', '--pvalue',
        action='store_true',
        help='''Shortcut for -c pvalue -s '(0,1)', useful for plotting
        p-values.''')
    heatmap_parser.add_argument(
        '-T', '--tetris',
        action='store_true',
        help='''Pass this flag to draw classified interactions in different
        colors. Overrides -c/--colormap and -s/--colorscale.''')
    heatmap_parser.add_argument(
        '-b', '--log_base',
        type=str,
        default='None',
        help='''Pass this flag to log the input data using the given base before
        visualizing. The default is None, which applies no logging.''')
    heatmap_parser.add_argument(
        '-e', '--pseudocount',
        type=float,
        default=1.0,
        help='''Pass this flag to specify a psuedocount to use before logging
        the data. The default is 1.0.''')
    heatmap_parser.add_argument(
        '-x', '--x_zoom',
        type=str,
        help='''Specify a genomic range to zoom in the x-axis on of the form
        'chr:start-end'. You must also pass -r/--region.''')
    heatmap_parser.add_argument(
        '-y', '--y_zoom',
        type=str,
        help='''Specify a genomic range to zoom in the y-axis on of the form
        'chr:start-end'. If you pass -x/--x_zoom but not -y/--y_zoom the zoom
        window is assumed to be on-diagonal (x- and y-axes are the same).''')
    heatmap_parser.add_argument(
        '-t', '--tracks',
        type=str,
        help='''Pass a comma-separated list of bigwig files to plot as chipseq
        tracks.''')
    heatmap_parser.add_argument(
        '-d', '--domains',
        type=str,
        help='''Pass a path to a bedfile of contact domains to outline them on
        the heatmap.''')
    heatmap_parser.set_defaults(func=heatmap_tool)


def heatmap_tool(parser, args):
    import glob

    import numpy as np

    from lib5c.tools.helpers import resolve_level, resolve_parallel, \
        split_self_regionally, resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.parsers.genes import load_genes
    from lib5c.parsers.bed import load_features
    from lib5c.plotters.colormaps import get_colormap
    from lib5c.plotters.heatmap import plot_heatmap
    from lib5c.plotters.queried_counts_heatmap import \
        plot_queried_counts_heatmap
    from lib5c.util.counts import extract_queried_counts, flip_pvalues, \
        regional_counts_to_pvalues, queried_counts_to_pvalues,\
        flatten_regional_counts, log_regional_counts, parallel_log_counts
    from lib5c.util.ast_eval import eval_expr
    from lib5c.util.bed import parse_feature_from_string
    from lib5c.util.slicing import slice_matrix_by_grange
    from lib5c.parsers.config import parse_config

    # resolve primerfile and level, load primermap
    primerfile = resolve_primerfile(args.infile, args.primerfile)
    primermap = load_primermap(primerfile)
    resolved_level = resolve_level(primermap, args.level)

    # -s shortcuts
    if args.scale == 'obs':
        args.scale = '(min,p98)'
    if args.scale == 'obs_over_exp':
        args.scale = '(mu-2.5*sigma,mu+2.5*sigma)'

    # special check between resolving the level and resolving parallel:
    # we will check to see if args.scale contains any of the keywords (min, max,
    # mu, sigma), and if it does we will parse all the counts and evaluate the
    # expression
    if args.scale is not None and\
            any(keyword in args.scale
                for keyword in ['min', 'max', 'mu', 'sigma', 'p95', 'p98']):
        if args.region is None:
            split_self_regionally(primermap.keys(), script='lib5c plot heatmap',
                                  hang=args.hang)
        print('precomputing scale for region %s' % args.region)
        expanded_infiles = glob.glob(args.infile)
        regional_counts_superdict = {
            infile: load_counts(infile, primermap)[args.region]
            for infile in expanded_infiles
        }
        if args.log_base != 'None':
            regional_counts_superdict = {
                infile: log_regional_counts(regional_counts_superdict[infile],
                                            pseudocount=args.pseudocount,
                                            base=args.log_base)
                for infile in expanded_infiles}
        flattened_regional_counts = {
            infile: flatten_regional_counts(regional_counts_superdict[infile],
                                            discard_nan=True)
            for infile in expanded_infiles}
        mus = [np.mean(flattened_regional_counts[infile])
               for infile in expanded_infiles]
        sigmas = [np.std(flattened_regional_counts[infile])
                  for infile in expanded_infiles]
        mins = [np.min(flattened_regional_counts[infile])
                for infile in expanded_infiles]
        maxs = [np.max(flattened_regional_counts[infile])
                for infile in expanded_infiles]
        p98s = [np.percentile(flattened_regional_counts[infile], 98)
                for infile in expanded_infiles]
        p95s = [np.percentile(flattened_regional_counts[infile], 95)
                for infile in expanded_infiles]
        variables = {'mu': np.mean(mus),
                     'sigma': np.mean(sigmas),
                     'min': np.mean(mins),
                     'max': np.mean(maxs),
                     'p95': np.mean(p95s),
                     'p98': np.mean(p98s)}
        pieces = map(str.strip, args.scale.strip('()').split(','))
        left = eval_expr(pieces[0], variables=variables)
        right = eval_expr(pieces[1], variables=variables)
        args.scale = '(%s,%s)' % (left, right)

    # resolve parallel
    resolve_parallel(parser, args, subcommand='plot heatmap')

    # load counts
    print('loading counts')
    counts = load_counts(args.infile, primermap)

    # support logging
    if args.log_base != 'None':
        counts = parallel_log_counts(counts, pseudocount=args.pseudocount,
                                     base=args.log_base)

    print('preparing to plot')
    # resolve region
    if args.region is not None:
        counts = counts[args.region]
        primermap = primermap[args.region]

    # compute queried counts if appropriate
    if resolved_level == 'fragment':
        counts, primermap_x, primermap_y = extract_queried_counts(counts,
                                                                  primermap)
    else:
        primermap_x = primermap
        primermap_y = primermap

    # parse colorscale from the parameter value
    if args.tetris:
        colorscale = None
    elif args.scale is None:
        if resolved_level == 'bin':
            counts = regional_counts_to_pvalues(counts)
        else:
            counts = queried_counts_to_pvalues(counts)
        counts = flip_pvalues(counts)
        colorscale = (0, 0.98)
    elif '(' in args.scale and ')' in args.scale and ',' in args.scale:
        colorscale = map(float, args.scale.strip('()').split(','))
    else:
        colorscale = parse_config(args.scale, 'colorscales')
        if args.region is not None:
            colorscale = colorscale[args.region]

    # resolve colormap
    if args.tetris:
        cmap = None
    elif args.pvalue:
        cmap = 'pvalue'
        colorscale = (0, 1)
    else:
        cmap = get_colormap(args.colormap)

    # resolve outfile
    if args.region:
        resolved_outfile = args.outfile
    else:
        resolved_outfile = {region: args.outfile.replace(r'%r', region)
                            for region in counts.keys()}

    # resolve genes
    if type(args.genes) == str and args.genes not in ['mm9', 'mm10', 'hg18',
                                                      'hg19', 'hg38']:
        genes_dict = load_genes(args.genes)
        if args.region:
            resolved_genes = genes_dict[primermap[0]['chrom']]
        else:
            resolved_genes = {region: genes_dict[primermap[region][0]['chrom']]
                              for region in primermap}
    else:
        resolved_genes = args.genes

    # resolve tracks
    resolved_tracks = map(str.strip, args.tracks.strip('()').split(',')) \
        if args.tracks is not None else None

    # resolve domains
    if args.domains is None:
        resolved_domains = None
    elif args.region is not None:
        resolved_domains = load_features(
            args.domains)[primermap[0]['chrom']]
    else:
        resolved_domains = {
            region: load_features(args.domains)[primermap[region][0]['chrom']]
            for region in primermap
        }

    # resolve zoom window query
    if args.region is not None and args.x_zoom is not None:
        grange_x = parse_feature_from_string(args.x_zoom)
        if args.y_zoom is not None:
            grange_y = parse_feature_from_string(args.y_zoom)
        else:
            grange_y = grange_x
        # this works only because args.region is defined, which means that
        # primermap_x and primermap_y are guaranteed to be regional here
        counts, grange_x, grange_y = slice_matrix_by_grange(
            counts, regional_primermap_x=primermap_x, grange_x=grange_x,
            regional_primermap_y=primermap_y, grange_y=grange_y)
    else:
        # everything below is technically wrong for fragment-level heatmaps,
        # but these variables are not passed to the fragment-level heatmap
        # plotter anyway
        if args.region is None:
            grange_x = {region: {'chrom': primermap[region][0]['chrom'],
                                 'start': primermap[region][0]['start'],
                                 'end': primermap[region][-1]['end']}
                        for region in primermap}
            grange_y = grange_x
        else:
            grange_x = {'chrom': primermap[0]['chrom'],
                        'start': primermap[0]['start'],
                        'end': primermap[-1]['end']}
            grange_y = grange_x

    # plot heatmap
    print('plotting')
    if resolved_level == 'bin':
        plot_heatmap(
            matrix=counts, grange_x=grange_x, grange_y=grange_y,
            rulers=args.rulers, genes=resolved_genes, colorscale=colorscale,
            colorbar=args.colorbar, colormap=cmap, tracks=resolved_tracks,
            domains=resolved_domains, outfile=resolved_outfile)
    else:
        plot_queried_counts_heatmap(
            counts, resolved_outfile, colorscale=colorscale,
            colorbar=args.colorbar, cmap=cmap)
