import argparse

from lib5c.tools.parents import primerfile_parser


def add_colorscale_tool(parser):
    colorscale_parser = parser.add_parser(
        'colorscale',
        prog='lib5c colorscale',
        help='compute regional colorscales for comparing replicates',
        parents=[primerfile_parser]
    )
    colorscale_parser.add_argument(
        'type',
        type=str,
        choices=['obs', 'obs_over_exp'],
        help='''Specify whether you want to compute an observed colorscale or an
        observed over expected colorscale.''')
    colorscale_parser.add_argument(
        'outfile',
        type=str,
        help='''Filename to save the computed colorscales to.''')
    colorscale_parser.add_argument(
        '-m', '--max_percentile',
        type=float,
        default=98,
        help='''When computing an observed colorscale, the percentile to use
        when computing the maximum end of the colorscale. Default is 98.''')
    colorscale_parser.add_argument(
        '-b', '--log_base',
        type=str,
        default='None',
        help='''Pass this flag to log the input data using the given base before
            computing. The default is None, which applies no logging.''')
    colorscale_parser.add_argument(
        '-e', '--pseudocount',
        type=float,
        default=1.0,
        help='''Pass this flag to specify a psuedocount to use before logging
            the data. The default is 1.0.''')
    colorscale_parser.add_argument(
        'countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''Countsfiles to compute colorscales for.''')
    colorscale_parser.set_defaults(func=colorscale_tool)


def colorscale_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.scales import compute_regional_obs_scale,\
        compute_regional_obs_over_exp_scale
    from lib5c.util.counts import parallel_log_counts
    from lib5c.writers.config import write_config

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

    # support logging
    if args.log_base != 'None':
        counts_superdict = {
            expanded_infile: parallel_log_counts(
                counts_superdict[expanded_infile], pseudocount=args.pseudocount,
                base=args.log_base)
            for expanded_infile in counts_superdict}

    if args.type == 'obs':
        colorscales = {
            region: compute_regional_obs_scale(
                counts_superdict, region, top_percentile=args.max_percentile)
            for region in primermap.keys()
        }
    else:
        colorscales = {
            region: compute_regional_obs_over_exp_scale(counts_superdict,
                                                        region)
            for region in primermap.keys()
        }

    # write config
    write_config(args.outfile, 'colorscales', colorscales)
