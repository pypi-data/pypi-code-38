import argparse

from lib5c.tools.parents import primerfile_parser


def add_threshold_tool(parser):
    threshold_parser = parser.add_parser(
        'threshold',
        prog='lib5c threshold',
        help='threshold p-values',
        parents=[primerfile_parser]
    )
    threshold_parser.add_argument(
        '-c', '--conditions',
        type=str,
        help='A comma-separated list of condition names.')
    threshold_parser.add_argument(
        '-t', '--significance_threshold',
        default=0.05,
        type=float,
        help='''The p-value or q-value to threshold significance with. Default
        is 0.05.''')
    threshold_parser.add_argument(
        '-B', '--bh_fdr',
        action='store_true',
        help='''Pass this flag to apply BH-FDR adjustment to p-values before
        applying the significance threshold.''')
    threshold_parser.add_argument(
        '-T', '--two_tail',
        action='store_true',
        help='''Pass this in combination with -B/--bh_fdr to apply HH-FDR to the
        two-tailed p-values, but only report the significant right-tail events
        as loops. Note that two-tailed p-values are only accurate if p-values
        were called using a continuous distribution.''')
    threshold_parser.add_argument(
        '-C', '--concordant',
        action='store_true',
        help='''Pass this flag to report only those interactions which are
        significant in all replicates for a given condition. Skip this flag to
        combine evidence from all replicates in a given condition.''')
    threshold_parser.add_argument(
        '-s', '--size_threshold',
        default=3,
        type=int,
        help='''Interactions within connected components smaller than this will
        not be called. Default is 3.''')
    threshold_parser.add_argument(
        '-d', '--distance_threshold',
        default=24000,
        type=int,
        help='''Interactions with interaction distance (in bp) shorter than this
        will not be called. Default is 24000.''')
    threshold_parser.add_argument(
        '-b', '--background_threshold',
        default=0.6,
        type=float,
        help='''The p-value threshold to use to call a background loop class.
        Default is 0.6.''')
    threshold_parser.add_argument(
        '-o', '--dataset_outfile',
        type=str,
        help='''Pass a filename to write the complete thresholded Dataset to
        disk.''')
    threshold_parser.add_argument(
        '-k', '--kappa_confusion_outfile',
        type=str,
        help='''Pass a filename to write kappa metrics and confusion matrices
        to.''')
    threshold_parser.add_argument(
        'outfile',
        type=str,
        help='''Filename to write final calls to.''')
    threshold_parser.add_argument(
        'pvalue_countsfiles',
        type=str,
        nargs=argparse.REMAINDER,
        help='''P-value countsfiles to threshold.''')
    threshold_parser.set_defaults(func=threshold_tool)


def threshold_tool(parser, args):
    import glob

    from lib5c.tools.helpers import resolve_primerfile, \
        infer_replicate_names
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.algorithms.thresholding import two_way_thresholding, kappa, \
        concordance_confusion, color_confusion, count_clusters

    # resolve conditions
    conditions = map(str.strip, args.conditions.strip('()').split(',')) \
        if args.conditions else None

    # resolve primerfile
    primerfile = resolve_primerfile(args.pvalue_countsfiles, args.primerfile)

    # expand infiles
    expanded_infiles = []
    for infile in args.pvalue_countsfiles:
        expanded_infiles.extend(glob.glob(infile))

    # compute rep_names
    rep_names = infer_replicate_names(
        expanded_infiles, as_dict=True, pattern=args.pvalue_countsfiles[0]
        if len(args.pvalue_countsfiles) == 1
        and '*' in args.pvalue_countsfiles[0] else None)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    pvalues_superdict = {rep_name: load_counts(file_name, primermap)
                         for file_name, rep_name in rep_names.items()}

    # perform thresholding
    print('thresholding')
    d = two_way_thresholding(
        pvalues_superdict,
        primermap,
        conditions=conditions,
        significance_threshold=args.significance_threshold,
        bh_fdr=args.bh_fdr,
        two_tail=args.two_tail,
        concordant=args.concordant,
        distance_threshold=args.distance_threshold,
        size_threshold=args.size_threshold,
        background_threshold=args.background_threshold
    )

    # write
    print('writing results')
    write_counts(d.counts(name='color'), args.outfile, primermap,
                 skip_zeros=True)

    if args.dataset_outfile is not None:
        d.save(args.dataset_outfile)

    if args.kappa_confusion_outfile is not None:
        with open(args.kappa_confusion_outfile, 'w') as handle:
            if all([len(d.cond_reps[cond]) == 2 for cond in d.conditions]):
                handle.write("Cohen's kappa within reps\n")
                handle.write('-------------------------\n')
                kappa_dict = kappa(d)
                for cond in kappa_dict:
                    handle.write('%s: %s\n' % (cond, kappa_dict[cond]))
                handle.write('\n')
                handle.write('concordance confusion matrices\n')
                handle.write('------------------------------\n')
                confusion_dict = concordance_confusion(d)
                for cond in confusion_dict:
                    handle.write('%s:\n' % cond)
                    handle.write(str(confusion_dict[cond]) + '\n')
                handle.write('\n')
            if len(d.conditions) == 2:
                handle.write('color confusion matrix\n')
                handle.write('----------------------\n')
                handle.write(str(color_confusion(d)) + '\n')
                handle.write('\n')
            handle.write('cluster counts\n')
            handle.write('--------------\n')
            color_counts = count_clusters(d)
            for color, count in color_counts.items():
                handle.write('%s: %i\n' % (color, count))
            handle.write('\n')
