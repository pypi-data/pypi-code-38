from lib5c.tools.parents import parallelization_parser, simple_in_out_parser, \
    primerfile_parser


def add_interaction_score_tool(parser):
    interaction_score_parser = parser.add_parser(
        'interaction-score',
        prog='lib5c interaction-score',
        help='convert p-values to interaction scores',
        parents=[primerfile_parser, parallelization_parser,
                 simple_in_out_parser]
    )
    interaction_score_parser.set_defaults(func=interaction_score_tool)


def interaction_score_tool(parser, args):
    from lib5c.tools.helpers import resolve_primerfile, resolve_parallel
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.counts import convert_pvalues_to_interaction_scores
    from lib5c.writers.counts import write_counts

    # resolve primerfile and parallel
    resolve_parallel(parser, args, subcommand='interaction-score')
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts = load_counts(args.infile, primermap)

    # convert pvalues to IS
    print('converting p-values to interaction scores')
    counts = convert_pvalues_to_interaction_scores(counts)

    # write output
    print('writing countsfiles')
    write_counts(counts, args.outfile, primermap)
