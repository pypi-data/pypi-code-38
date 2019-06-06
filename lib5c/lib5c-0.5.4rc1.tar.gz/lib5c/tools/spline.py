from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, primerfile_parser


def add_spline_tool(parser):
    spline_parser = parser.add_parser(
        'spline',
        prog='lib5c spline',
        help='spline normalization',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    spline_parser.add_argument(
        '-J', '--joint_normalize',
        action='store_true',
        help='''Normalize all input files using a single shared bias model.''')
    spline_parser.add_argument(
        '-b', '--bias_factors',
        type=str,
        default='(% GC,length)',
        help='''The list of bias factors to fit splines for. The default is
        "(%% GC,length)".''')
    spline_parser.add_argument(
        '-k', '--knots',
        type=str,
        default='(0,10)',
        help='''The number of knots to put in the splines. Pass a list of the
        form "(k_1,k_2,k_3)" to use a different number of knots for the
        different bias factors. If a bias factor is discrete, pass 0 for its
        knot number to use an empirical discrete surface instead of a spline.
        The default is '(0,10)'.''')
    spline_parser.add_argument(
        '-e', '--epsilon',
        type=float,
        default=1e-4,
        help='''The maximum relative change in each bias model between
        successive iterations before declaring convergence. The default is
        1e-4.''')
    spline_parser.add_argument(
        '-i', '--max_iterations',
        type=int,
        default=100,
        help='''Maximum number of iterations. The default is 100.''')
    spline_parser.add_argument(
        '-o', '--model_outfile',
        type=str,
        help='''Pass a string reference to a path to which to write the splines
        as a pickle.''')
    spline_parser.add_argument(
        '-m', '--expected_model',
        type=str,
        help='''Pass a string reference to a countsfile containing the expected
        model to be used. If this is not passed, a linear log-log fit will be
        used.''')
    spline_parser.add_argument(
        '-U', '--unlog',
        action='store_true',
        help='''Pass this flag to fit the splines on unlogged counts. By
        default, they will be fit to logged counts.''')
    spline_parser.add_argument(
        '-A', '--asymmetric',
        action='store_true',
        help='''Pass this flag to consider only the upper triangular entries of
        the contact matrices.''')
    spline_parser.set_defaults(func=spline_tool)


def spline_tool(parser, args):
    import glob
    import pickle

    from lib5c.tools.helpers import resolve_parallel, infer_replicate_names, \
        resolve_primerfile, resolve_expected_models
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.algorithms.spline_normalization import \
        iterative_spline_normalization
    from lib5c.util.system import check_outdir

    # resolve parallel and primerfile
    primerfile = resolve_primerfile(args.infile, args.primerfile)
    if not args.joint_normalize:
        resolve_parallel(parser, args, subcommand='spline')

    # load counts
    print('loading counts')
    infiles = glob.glob(args.infile)
    primermap = load_primermap(primerfile)
    observed_counts = [load_counts(infile, primermap) for infile in infiles]

    # resolve expected model
    expected_counts = resolve_expected_models(
        args.expected_model, observed_counts, primermap, level=args.level)

    # resolve bias factors
    resolved_bias_factors = map(
        str.strip, args.bias_factors.strip('()').split(','))

    # resolve knots
    try:
        resolved_knots = int(args.knots)
    except ValueError:
        resolved_knots = map(int, args.knots.strip('()').split(','))

    # fit splines
    print('fitting splines')
    splines, _, corrected = iterative_spline_normalization(
        observed_counts, expected_counts, primermap, resolved_bias_factors,
        max_iter=args.max_iterations, eps=args.epsilon, knots=resolved_knots,
        log=not args.unlog, asymmetric=args.asymmetric)

    # save splines
    if args.model_outfile is not None:
        check_outdir(args.model_outfile)
        with open(args.model_outfile, 'wb') as handle:
            pickle.dump(splines, handle)

    # write counts
    print('writing counts')
    if not args.joint_normalize:
        write_counts(corrected[0], args.outfile, primermap)
    else:
        replicate_names = infer_replicate_names(
            infiles, pattern=args.infile if '*' in args.infile else None)
        outfiles = [args.outfile.replace(r'%s', rep) for rep in replicate_names]
        for i in range(len(corrected)):
            write_counts(corrected[i], outfiles[i], primermap)
