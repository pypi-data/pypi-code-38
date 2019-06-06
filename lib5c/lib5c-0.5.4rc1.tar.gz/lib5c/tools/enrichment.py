from lib5c.tools.parents import primerfile_parser


def add_enrichment_tool(parser):
    enrichment_parser = parser.add_parser(
        'enrichment',
        prog='lib5c plot enrichment',
        help='plot enrichments',
        parents=[primerfile_parser]
    )
    enrichment_parser.add_argument(
        'infile',
        type=str,
        help='''A countsfile whose values are looptypes as strings.''')
    enrichment_parser.add_argument(
        'outfile',
        type=str,
        help='''The file to write the plot to. %%s in the filename may be
        replaced if called with '-a all' or '-l all', see below.''')
    enrichment_parser.add_argument(
        '-d', '--annotations_dir',
        type=str,
        default='./annotations',
        help='''Directory containing annotation bedfiles. Default is
        './annotations'.''')
    enrichment_parser.add_argument(
        '-a', '--annotation',
        type=str,
        help='''Pass an annotation to hold it fixed and vary the looptype on the
        x axis and the annotation being looped to on the y axis of the heatmap.
        Pass 'all' to draw one plot for every annotation; %%s in the outfile
        will be replaced with the annotation.''')
    enrichment_parser.add_argument(
        '-l', '--looptype',
        type=str,
        help='''Pass a looptype to hold it fixed and vary the annotations on
        both axes of the heatmap. Pass 'all' to draw one plot for every
        looptype; %%s in the outfile will be replaced with the looptype.''')
    enrichment_parser.add_argument(
        '-ao', '--annotation_order',
        type=str,
        help='''Set the subset and order of annotations to plot.''')
    enrichment_parser.add_argument(
        '-lo', '--looptype_order',
        type=str,
        help='''Set the subset and order of looptypes to plot.''')
    enrichment_parser.add_argument(
        '-m', '--margin',
        type=int,
        default=1,
        help='''The 'margin for error' for annotation intersections, in bin
        units. Default is 1.''')
    enrichment_parser.add_argument(
        '-v', '--vmax',
        type=float,
        default=2.0,
        help='''The value to use for the vmax of the colorscale. The vmin will
        be set to the opposite of this value. Default is 2.0.''')
    enrichment_parser.set_defaults(func=enrichment_tool)


def enrichment_tool(parser, args):
    import numpy as np

    from lib5c.tools.helpers import resolve_primerfile
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.util.annotationmap import make_annotationmaps
    from lib5c.plotters.enrichment import plot_looptype_vs_annotation_heatmap, \
        plot_annotation_vs_annotation_heatmap

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.infile, args.primerfile)

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    looping_classes = load_counts(args.infile, primermap)

    # load annotations
    print('loading annotations')
    annotationmaps = make_annotationmaps(primermap,
                                         directory=args.annotations_dir)

    # resolve looptype_order and annotation_order
    looptype_order = map(str.strip, args.looptype_order.strip('()').split(','))\
        if args.looptype_order is not None else None
    annotation_order = map(
        str.strip, args.annotation_order.strip('()').split(','))\
        if args.annotation_order is not None else None

    # plot enrichments
    print('plotting enrichments')
    if args.annotation is not None:
        if args.annotation == 'all':
            constant_annotations = annotationmaps.keys()
            outfiles = [args.outfile % c for c in constant_annotations]
        else:
            constant_annotations = [args.annotation]
            outfiles = [args.outfile]
        for c, o in zip(constant_annotations, outfiles):
            plot_looptype_vs_annotation_heatmap(
                annotationmaps,
                looping_classes,
                constant_annotation=c,
                loop_type_order=looptype_order,
                annotation_order=annotation_order,
                margin=args.margin,
                vmin=-args.vmax,
                vmax=args.vmax,
                outfile=o
            )
    elif args.looptype is not None:
        if args.looptype == 'all':
            looptypes = list(reduce(
                set.union, [np.unique(looping_classes[region])
                            for region in looping_classes],
                set()) - {''})
            outfiles = [args.outfile % l for l in looptypes]
        else:
            looptypes = [args.looptype]
            outfiles = [args.outfile]
        for l, o in zip(looptypes, outfiles):
            plot_annotation_vs_annotation_heatmap(
                annotationmaps,
                looping_classes,
                loop_type=l,
                axis_order=annotation_order,
                margin=args.margin,
                vmin=-args.vmax,
                vmax=args.vmax,
                outfile=o
            )
