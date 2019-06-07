import argparse

from lib5c.tools.parents import primerfile_parser


def add_remove_tool(parser):
    remove_parser = parser.add_parser(
        'remove',
        prog='lib5c remove',
        help='remove low-count primer-primer pairs',
        parents=[primerfile_parser]
    )
    remove_parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=5.0,
        help='''Sets the threshold. A rep passes the threshold if it is greater
        than or equal to this number. The default is 5.0.''')
    remove_parser.add_argument(
        '-n', '--num_reps',
        type=int,
        help='''Pass an int to make the condition for removal be that this many
        reps must fail the threshold. This overrides the -f/--fraction_reps
        flag.''')
    remove_parser.add_argument(
        '-f', '--fraction_reps',
        type=float,
        help='''Pass a fraction (between 0 and 1) as a float to make the
        condition for removal be that this fraction of the reps must fail the
        threshold.''')
    remove_parser.add_argument(
        '-A', '--all_reps',
        action='store_true',
        help='''Pass this flag to make the condition be that the sum across all
        replicates must clear the threshold. This is the default mode if niether
        -n/--num_reps nor -f/--fraction_reps is passed.''')
    remove_parser.add_argument(
        'outfile_pattern',
        type=str,
        help='''Pattern describing where to write output countsfiles to. %%s
        will be replaced by the replicate name.''')
    remove_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to use to determine which primer-primer pairs should
        be removed.''')
    remove_parser.set_defaults(func=remove_tool)


def remove_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, infer_replicate_names
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.algorithms.outliers import remove_primer_primer_pairs

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

    # remove primer-primer pairs
    print('removing low primer-primer pairs')
    remove_primer_primer_pairs(
        counts_superdict, primermap, threshold=args.threshold,
        num_reps=args.num_reps, fraction_reps=args.fraction_reps,
        all_reps=args.all_reps)

    # write output
    print('writing output')
    replicate_names = infer_replicate_names(
        expanded_infiles, pattern=args.countsfiles[0]
        if len(args.countsfiles) == 1 and '*' in args.countsfiles[0] else None)
    for i in range(len(expanded_infiles)):
        outfile = args.outfile_pattern % replicate_names[i]
        write_counts(counts_superdict[expanded_infiles[i]], outfile, primermap)
