from lib5c.tools.parents import simple_in_out_parser, parallelization_parser, \
    primerfile_parser


def add_iced_tool(parser):
    iced_parser = parser.add_parser(
        'iced',
        prog='lib5c iced',
        help='iced balancing normalization',
        parents=[primerfile_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    iced_parser.add_argument(
        '-B', '--output_bias',
        action='store_true',
        help='''If this flag is present, the bias vectors will be written to
        .bias files located next to the output .counts files.''')
    iced_parser.add_argument(
        '-e', '--epsilon',
        type=float,
        default=1e-4,
        help='''The relative improvement in the residual before declaring
        convergence. The default is 1e-4.''')
    iced_parser.add_argument(
        '-i', '--max_iterations',
        type=int,
        default=3000,
        help='''Maximum number of iterations. The default is 3000.''')
    iced_parser.add_argument(
        '-n', '--norm',
        type=str,
        default='l1',
        choices=['l1', 'l2'],
        help='''Norm to use as a distance metric. The default is 'l1'.''')
    iced_parser.add_argument(
        '-s', '--imputation_size',
        type=int,
        default=0,
        help='''Size of window, in units of matrix indices, to use to impute nan
        values in the original counts matrix. Pass 0 to skip imputation, which
        is the default behavior.''')
    iced_parser.set_defaults(func=iced_tool)


def iced_tool(parser, args):
    import os

    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.contrib.iced.balancing import iced_balance_matrix
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.writers.bias import write_cis_bias_vector

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='iced')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # express normalize
    print('iced balancing')
    balanced_counts, bias_factors = iced_balance_matrix(
        counts, max_iter=args.max_iterations, eps=args.epsilon, norm=args.norm,
        imputation_size=args.imputation_size)

    # write counts
    print('writing counts')
    write_counts(balanced_counts, args.outfile, primermap)

    # write bias vector
    if args.output_bias:
        print('writing bias vector')
        write_cis_bias_vector(bias_factors, primermap, '%s.bias' %
                              os.path.splitext(args.outfile)[0])
