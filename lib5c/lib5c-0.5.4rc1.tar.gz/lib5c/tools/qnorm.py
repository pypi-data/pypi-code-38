import argparse

from lib5c.tools.parents import primerfile_parser


def add_qnorm_tool(parser):
    qnorm_parser = parser.add_parser(
        'qnorm',
        prog='lib5c qnorm',
        help='quantile normalization',
        parents=[primerfile_parser]
    )
    qnorm_parser.add_argument(
        '-A', '--average',
        action='store_true',
        help='''Pass this flag to set all tied entries to the average value
        across the tied ranks. The default is to set all tied entries to the
        value of the lowest rank.''')
    qnorm_parser.add_argument(
        '-R', '--regional',
        action='store_true',
        help='''Pass this flag to apply quantile normalization to each
        region separately.''')
    qnorm_parser.add_argument(
        '-c', '--condition_on',
        type=str,
        help='''Specify a locus property to perform quantile normalization
        conditioning on that property. Only works with -R/--regional.''')
    qnorm_parser.add_argument(
        '-r', '--reference',
        type=str,
        help='''Specify a countsfile or a replicate name to use as a reference
        distribution.''')
    qnorm_parser.add_argument(
        'outfile_pattern',
        type=str,
        help='''Pattern to use to name output files. %%s will be replaced with
        the replicate name, as guessed from the input files.''')
    qnorm_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to quantile normalize.''')
    qnorm_parser.set_defaults(func=qnorm_tool)


def qnorm_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, infer_replicate_names
    from lib5c.algorithms.qnorm import qnorm_counts_superdict
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts

    # resolve primerfile
    primerfile = resolve_primerfile(args.countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    counts_superdict = {infile: load_counts(infile, primermap)
                        for infile in expanded_infiles}

    # resolve tie
    resolved_tie = 'average' if args.average else 'lowest'

    # resolve reference
    if args.reference is None:
        resolved_reference = None
    else:
        if args.reference not in counts_superdict:
            # maybe it's a partial replicate name
            partial_match = False
            for infile in counts_superdict:
                if args.reference in infile:
                    resolved_reference = infile
                    partial_match = True
                    break
            if not partial_match:
                # no partial match, try to load it as a new countsfile
                counts_superdict[args.reference] = load_counts(args.reference,
                                                               primermap)
                resolved_reference = args.reference
        else:
            resolved_reference = args.reference

    # quantile normalize
    print('quantile normalizing')
    qnormed_counts_superdict = qnorm_counts_superdict(
        counts_superdict,
        primermap,
        tie=resolved_tie,
        regional=args.regional,
        condition_on=args.condition_on,
        reference=resolved_reference
    )

    # write counts
    print('writing counts')
    replicate_names = infer_replicate_names(
        expanded_infiles, pattern=args.countsfiles[0]
        if len(args.countsfiles) == 1 and '*' in args.countsfiles[0] else None)
    outfiles = {expanded_infiles[i]:
                args.outfile_pattern.replace(r'%s', replicate_names[i])
                for i in range(len(expanded_infiles))}
    for infile in expanded_infiles:
        write_counts(qnormed_counts_superdict[infile], outfiles[infile],
                     primermap)
