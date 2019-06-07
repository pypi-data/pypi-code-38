from lib5c.tools.parents import level_parser, parallelization_parser, \
    distribution_parser, primerfile_parser


def add_pvalues_tool(parser):
    pvalues_parser = parser.add_parser(
        'pvalues',
        help='call pvalues for interactions',
        parents=[primerfile_parser, level_parser, parallelization_parser,
                 distribution_parser]
    )
    pvalues_parser.add_argument(
        'observed',
        type=str,
        help='''File containing observed counts for which p-values should be
        called.''')
    pvalues_parser.add_argument(
        'expected',
        type=str,
        help='''File containing expected counts.''')
    pvalues_parser.add_argument(
        'outfile',
        type=str,
        help='''Path to file to write p-value counts to.''')
    pvalues_parser.add_argument(
        '-b', '--bias_vector',
        type=str,
        help='''File containing a bias vector. If this flag is present, the
        p-value computation will be performed in deconvoluted space.''')
    pvalues_parser.set_defaults(func=pvalues_tool)


def pvalues_tool(parser, args):
    from lib5c.tools.helpers import resolve_parallel, resolve_primerfile
    from lib5c.parsers.bias import load_bias_vector
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.algorithms.distributions_legacy.fitting import fit_and_call

    # resolve parallel and primerfile
    resolve_parallel(parser, args, subcommand='pvalues', key_arg='observed')
    primerfile = resolve_primerfile(args.observed, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    observed_counts = load_counts(args.observed, primermap)
    expected_counts = load_counts(args.expected, primermap)

    # load bias vector
    if args.bias_vector is not None:
        print('loading bias vector')
        bias = load_bias_vector(args.bias_vector, primermap)
    else:
        bias = {region: None for region in observed_counts.keys()}

    # fit distributions
    print('fitting and calling')
    pvalues = fit_and_call(observed_counts, expected_counts, mode=args.mode,
                           dist=args.distribution, log=args.log, bias=bias)

    # write p-values
    print('writing p-values')
    write_counts(pvalues, args.outfile, primermap)
