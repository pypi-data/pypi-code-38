def add_determine_bins_tool(parser):
    determine_bins_parser = parser.add_parser(
        'determine-bins',
        prog='lib5c determine-bins',
        help='create binfiles from primerfiles',
    )
    determine_bins_parser.add_argument(
        'primerfile',
        type=str,
        help='''File describing the primerset to determine bins for.''')
    determine_bins_parser.add_argument(
        'binfile',
        type=str,
        help='''Path to file to write the resulting binfile to.''')
    determine_bins_parser.add_argument(
        '-w', '--bin_width',
        type=int,
        default=4000,
        help='''Width of the bins to tile across the regions, in bp. Default is
        4000.''')
    determine_bins_parser.add_argument(
        '-s', '--region_span',
        type=str,
        choices=['mid-to-mid', 'start-to-end'],
        default='mid-to-mid',
        help='''Describes whether the span of the region is considered to be
        stretching from the midpoint of the first fragment to the midpoint of
        the last fragment ('mid-to-mid') or from the beginning of the first
        fragment to the end of the last fragment ('start-to-end'). Default is
        'mid-to-mid'.''')
    determine_bins_parser.add_argument(
        '-n', '--bin_number',
        type=str,
        choices=['n', 'n+1'],
        default='n',
        help='''Describes how many bins to fit in the region, given that 'n' is
        the largest number of full bins that will fit in the region. Pass 'n' to
        reproduce traditional pipeline output, at the risk of leaving some
        fragment midpoints outside of the range of the bins. Use 'n+1' for a
        more conservative binning strategy that is guaranteed to not leave any
        fragment midpoints outside of the region if -s/--region_span is
        'mid-to-mid'. Default is 'n'.''')
    determine_bins_parser.set_defaults(func=determine_bins_tool)


def determine_bins_tool(parser, args):
    from lib5c.parsers.primers import load_primermap
    from lib5c.writers.primers import write_primermap
    from lib5c.algorithms.determine_bins import determine_regional_bins

    # load primermap
    primermap = load_primermap(args.primerfile)

    # make bins
    pixelmap = determine_regional_bins(
        primermap,
        args.bin_width,
        region_name={region: region for region in primermap.keys()},
        region_span=args.region_span,
        bin_number=args.bin_number
    )

    # write bins
    write_primermap(pixelmap, args.binfile)
