from lib5c.tools.parents import simple_in_out_parser, filter_parser, \
    parallelization_parser


def add_bin_tool(parser):
    bin_parser = parser.add_parser(
        'bin',
        prog='lib5c bin',
        help='bin fragment-level counts',
        parents=[simple_in_out_parser, filter_parser, parallelization_parser]
    )
    bin_parser.add_argument(
        '-p', '--primerfile',
        type=str,
        help='''Primer file to use. If this flag is not present, the first .bed
        file whose filename contains the substring 'primer' next to the .counts
        file specified in countsfile will be used.''')
    bin_parser.add_argument(
        '-b', '--binfile',
        type=str,
        help='''Bin file to use. If this flag is not present, the first .bed
        file whose filename contains the substring 'bin' next to the .counts
        file specified in infiles will be used.''')
    bin_parser.set_defaults(func=bin_tool)


def bin_tool(parser, args):
    import glob
    import os

    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.util.primers import guess_bin_step
    from lib5c.tools.helpers import resolve_parallel
    from lib5c.algorithms.filtering.filter_functions import make_filter_function
    from lib5c.algorithms.filtering.fragment_bin_filtering import \
        fragment_bin_filter
    from lib5c.algorithms.filtering.unsmoothable_columns import \
        wipe_unsmoothable_columns

    resolve_parallel(parser, args, subcommand='bin')

    # resolve primerfile
    if args.primerfile is None:
        resolved_primerfile = glob.glob(
            os.path.join(os.path.split(args.infile)[0], '*primer*.bed'))[0]
    else:
        resolved_primerfile = args.primerfile

    # resolve binfile
    if args.binfile is None:
        resolved_binfile = glob.glob(
            os.path.join(os.path.split(args.infile)[0], '*bin*.bed'))[0]
    else:
        resolved_binfile = args.binfile

    # get primermap and pixelmap
    pixelmap = load_primermap(resolved_binfile)
    primermap = load_primermap(resolved_primerfile)

    # resolve sigma and norm_order
    resolved_sigma = args.sigma if args.sigma is not None else args.window_width
    resolved_norm_order = args.norm_order is not None if args.norm_order else 1

    # construct filter function
    filter_function = make_filter_function(
        function=args.function,
        threshold=args.threshold,
        norm_order=resolved_norm_order,
        bin_width=guess_bin_step(pixelmap[pixelmap.keys()[0]]),
        sigma=resolved_sigma,
        inverse=args.inverse,
        gaussian=args.gaussian
    )

    # load counts
    counts = load_counts(args.infile, primermap)

    # smooth counts
    filtered_counts = fragment_bin_filter(
        counts, filter_function, pixelmap, primermap, args.window_width / 2,
        midpoint=args.midpoint)

    # honor -W/--wipe_unsmoothable_columns
    if args.wipe_unsmoothable_columns:
        filtered_counts = wipe_unsmoothable_columns(
            filtered_counts, primermap, pixelmap, args.window_width,
            midpoint=args.midpoint)

    # write counts
    write_counts(filtered_counts, args.outfile, pixelmap)
