import argparse

from lib5c.tools.parents import primerfile_parser


def add_pca_tool(parser):
    pca_parser = parser.add_parser(
        'pca',
        prog='lib5c plot pca',
        help='perform principal component analysis',
        parents=[primerfile_parser]
    )
    pca_parser.add_argument(
        '-c', '--csv',
        type=str,
        help='''Specify an output file to write output as csv.''')
    pca_parser.add_argument(
        '-i', '--image',
        type=str,
        help='''Specify an output file to write output as image.''')
    pca_parser.add_argument(
        '-s', '--separate_colors',
        type=str,
        help='''Specify a shell-quoted, comma-separated list of class names
        (which must be substrings of the replicate names) to color-code the
        output with. For example, 'ES,NPC'.''')
    pca_parser.add_argument(
        '-x', '--x_component',
        type=int,
        default=0,
        help='''Principal component to plot on the x-axis (zero-indexed). The
        default is 0.''')
    pca_parser.add_argument(
        '-y', '--y_component',
        type=int,
        default=1,
        help='''Principal component to plot on the y-axis (zero-indexed). The
        default is 1.''')
    pca_parser.add_argument(
        '-n', '--n_components',
        type=int,
        help='''Specify a number of components to plot in a pairwise grid
        instead of specifying only one x_component, y_component pair.''')
    pca_parser.add_argument(
        '-S', '--scale',
        action='store_true',
        help='''Pass this flag to scale the features to unit variance.''')
    pca_parser.add_argument(
        '-L', '--log',
        action='store_true',
        help='''Pass this flag to log the features.''')
    pca_parser.add_argument(
        '-a', '--algorithm',
        type=str,
        default='pca',
        choices=['pca', 'ica', 'fa', 'mds'],
        help='''Specify what algorithm to use. The default is 'pca' for standard
        principal component analysis.''')
    pca_parser.add_argument(
        '-f', '--polynomial_features',
        type=int,
        default=1,
        help='''Specify the degree of pure polynomial features to add to the
        design matrix. The default is 1, which includes only the original,
        linear features.''')
    pca_parser.add_argument(
        '-k', '--kernel',
        type=str,
        choices=['none', 'linear', 'poly', 'rbf', 'sigmoid', 'cosine'],
        help='''Specify a kernel to perform kernel PCA with. The default is
        'none', which does not perform kernel PCA.''')
    pca_parser.add_argument(
        '-d', '--degree',
        type=int,
        default=3,
        help='''Specify the degree to use when performing polynomial KPCA. The
        default is 3.''')
    pca_parser.add_argument(
        '-g', '--gamma',
        type=float,
        help='''Specify the value of the kernel coefficient gamma to use when
        performing radial basis function or polynomial KPCA. The default is to
        use 1/n_features.''')
    pca_parser.add_argument(
        '-b', '--bias_term',
        type=float,
        help='''Specify the independent term to use when performing polynomial
        or sigmoid KPCA. The default is 1 for polynomial kernels and 0 for
        sigmoid kernels.''')
    pca_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to perform PCA on.''')
    pca_parser.set_defaults(func=pca_tool)


def pca_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, infer_replicate_names,\
        infer_level_mapping
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.algorithms.pca import compute_pca_from_counts_superdict
    from lib5c.writers.pca import write_pca
    from lib5c.plotters.pca import plot_pca, plot_multi_pca

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts_superdict = {expanded_infile: load_counts(expanded_infile, primermap)
                        for expanded_infile in expanded_infiles}

    # compute labels
    rep_names = infer_replicate_names(
        expanded_infiles, pattern=args.countsfiles[0]
        if len(args.countsfiles) == 1 and '*' in args.countsfiles[0] else None)

    # determine levels
    levels = None
    if args.separate_colors is not None:
        levels = infer_level_mapping(
            rep_names, map(str.strip, args.separate_colors.split(',')))

    # resolve kernel_kwargs
    kernel_kwargs = {}
    if args.degree is not None:
        kernel_kwargs['degree'] = args.degree
    if args.gamma is not None:
        kernel_kwargs['gamma'] = args.gamma
    if args.bias_term is not None:
        kernel_kwargs['coef0'] = args.bias_term

    # perform PCA
    proj, pve, pcs = compute_pca_from_counts_superdict(
        counts_superdict, rep_order=expanded_infiles, scaled=args.scale,
        logged=args.log, kernel=args.kernel, kernel_kwargs=kernel_kwargs,
        variant=args.algorithm, pf=args.polynomial_features)

    # write csv
    if args.csv is not None:
        write_pca(args.csv, proj, rep_names=rep_names, pve=pve)

    # plot
    if args.image is not None:
        if args.n_components is not None:
            plot_multi_pca(proj, pcs=args.n_components, labels=rep_names,
                           levels=levels, outfile=args.image)
        else:
            plot_pca(proj, pcs=(args.x_component, args.y_component),
                     labels=rep_names, levels=levels, outfile=args.image)
