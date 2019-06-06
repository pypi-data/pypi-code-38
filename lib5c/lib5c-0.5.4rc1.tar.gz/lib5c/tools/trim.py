import argparse

from lib5c.tools.parents import primerfile_parser


def add_trim_tool(parser):
    trim_parser = parser.add_parser(
        'trim',
        prog='lib5c trim',
        help='primer and countsfile trimming',
        parents=[primerfile_parser]
    )
    trim_parser.add_argument(
        '-s', '--minimum_sum',
        type=int,
        default=100,
        help='''The minumum sum of cis contacts that a primer must have to avoid
        being trimmed. Pass 0 to skip this check. The default is 100.''')
    trim_parser.add_argument(
        '-f', '--minimum_fraction',
        type=float,
        default=0.5,
        help='''The minimum fraction of nonzero cis contacts that a primer must
        have to avoid being trimmed. Pass 0.0 to skip this check. The default is
        0.5.''')
    trim_parser.add_argument(
        '-w', '--wipe_countsfiles',
        type=str,
        help='''If this flag is present, output countsfiles will be written here
        with nan's at all removed positions. Pass a path containing one %%s,
        which will be replaced with the replicate name.''')
    trim_parser.add_argument(
        '-t', '--trim_countsfiles',
        type=str,
        help='''If this flag is present, output countsfiles will be written here
        with all trimmed positions removed. Pass a path containing one %%s,
        which will be replaced with the replicate name.''')
    trim_parser.add_argument(
        'outfile',
        type=str,
        help='''Path to file to write trimmed primers to.''')
    trim_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to use to determine which primers should be
        trimmed.''')
    trim_parser.set_defaults(func=trim_tool)


def trim_tool(parser, args):
    import os
    import glob

    from lib5c.tools.helpers import resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.writers.primers import write_primermap
    from lib5c.algorithms.trimming import trim_primers, wipe_counts, trim_counts

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # load counts
    primermap = load_primermap(primerfile)
    counts_superdict = {expanded_infile: load_counts(expanded_infile, primermap)
                        for expanded_infile in expanded_infiles}

    # trim primers
    trimmed_primermap, removed_indices = trim_primers(
        primermap, counts_superdict, min_sum=args.minimum_sum,
        min_frac=args.minimum_fraction)

    # write trimmed primermap
    write_primermap(trimmed_primermap, args.outfile)

    # wipe countsfiles
    if args.wipe_countsfiles is not None:
        for expanded_infile in expanded_infiles:
            # wipe counts
            wiped_counts = wipe_counts(counts_superdict[expanded_infile],
                                       removed_indices)

            # deduce outfile
            rep = os.path.splitext(os.path.split(expanded_infile)[1])[0]
            outfile = args.wipe_countsfiles % rep

            # write wiped output
            write_counts(wiped_counts, outfile, primermap)

    # trim countsfiles
    if args.trim_countsfiles is not None:
        for expanded_infile in expanded_infiles:
            # trim counts
            trimmed_counts = trim_counts(counts_superdict[expanded_infile],
                                         removed_indices)

            # deduce outfile
            rep = os.path.splitext(os.path.split(expanded_infile)[1])[0]
            outfile = args.trim_countsfiles % rep

            # write wiped output
            write_counts(trimmed_counts, outfile, trimmed_primermap)
