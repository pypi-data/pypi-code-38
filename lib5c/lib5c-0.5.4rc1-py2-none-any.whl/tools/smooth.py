from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    filter_parser, parallelization_parser, primerfile_parser


def add_smooth_tool(parser):
    smooth_parser = parser.add_parser(
        'smooth',
        help='smooth counts',
        prog='lib5c smooth',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 filter_parser, parallelization_parser]
    )
    smooth_parser.set_defaults(func=smooth_tool)


def smooth_tool(parser, args):
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.util.primers import guess_bin_step
    from lib5c.tools.helpers import resolve_level, resolve_parallel, \
        resolve_primerfile
    from lib5c.algorithms.filtering.filter_functions import make_filter_function
    from lib5c.algorithms.filtering.fragment_fragment_filtering import \
        fragment_fragment_filter
    from lib5c.algorithms.filtering.bin_bin_filtering import bin_bin_filter
    from lib5c.algorithms.filtering.unsmoothable_columns import \
        wipe_prebinned_unsmoothable_columns

    # resolve parallel, primerfile, and level and load primermap
    resolve_parallel(parser, args, subcommand='smooth')
    primerfile = resolve_primerfile(args.infile, args.primerfile)
    primermap = load_primermap(primerfile)
    resolved_level = resolve_level(primermap, args.level)

    # resolve sigma and norm_order
    resolved_sigma = args.sigma if args.sigma is not None else args.window_width
    resolved_norm_order = args.norm_order is not None if args.norm_order else 1

    # resolve bin step
    if resolved_level == 'bin':
        resolved_bin_step = guess_bin_step(primermap[primermap.keys()[0]])
    else:
        resolved_bin_step = 4000

    # construct filter function
    filter_function = make_filter_function(
        function=args.function,
        threshold=args.threshold,
        norm_order=resolved_norm_order,
        bin_width=resolved_bin_step,
        sigma=resolved_sigma,
        inverse=args.inverse,
        gaussian=args.gaussian
    )

    # load counts
    counts = load_counts(args.infile, primermap)

    # smooth counts
    if resolved_level == 'fragment':
        filtered_counts = fragment_fragment_filter(
            counts, filter_function, primermap, args.window_width / 2,
            midpoint=args.midpoint)
    else:
        filtered_counts = bin_bin_filter(
            counts, filter_function, primermap, args.window_width / 2)

    # honor -W/--wipe_unsmoothable_columns
    if args.wipe_unsmoothable_columns and resolved_level == 'bin':
        filtered_counts = wipe_prebinned_unsmoothable_columns(
            filtered_counts, counts, primermap, args.window_width)

    # write counts
    write_counts(filtered_counts, args.outfile, primermap)
