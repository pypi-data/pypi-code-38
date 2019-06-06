from lib5c.tools.parents import simple_in_out_parser, parallelization_parser, \
    primerfile_parser


def add_kr_tool(parser):
    kr_parser = parser.add_parser(
        'kr',
        prog='lib5c kr',
        help='knight-ruiz matrix balancing normalization',
        parents=[primerfile_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    kr_parser.add_argument(
        '-B', '--output_bias',
        action='store_true',
        help='''If this flag is present, the bias vectors will be written to
        .bias files located next to the output .counts files.''')
    kr_parser.add_argument(
        '-i', '--max_iterations',
        type=int,
        default=3000,
        help='''Maximum number of iterations. The default is 3000.''')
    kr_parser.add_argument(
        '-s', '--imputation_size',
        type=int,
        default=0,
        help='''Size of window, in units of matrix indices, to use to impute nan
        values in the original counts matrix. Pass 0 to skip imputation, which
        is the default behavior.''')
    kr_parser.set_defaults(func=kr_tool)


def kr_tool(parser, args):
    import os

    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.algorithms.knight_ruiz import kr_balance_matrix
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.writers.bias import write_cis_bias_vector

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='kr')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # express normalize
    print('kr balancing')
    balanced_counts, bias_vectors, errs = kr_balance_matrix(
        counts, max_iter=args.max_iterations,
        imputation_size=args.imputation_size)

    # write counts
    print('writing counts')
    write_counts(balanced_counts, args.outfile, primermap)

    # write bias vector
    if args.output_bias:
        print('writing bias vector')
        write_cis_bias_vector(bias_vectors, primermap, '%s.bias' %
                              os.path.splitext(args.outfile)[0])
