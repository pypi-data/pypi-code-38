from lib5c.tools.parents import level_parser, simple_in_out_parser, \
    parallelization_parser, primerfile_parser


def add_express_tool(parser):
    express_parser = parser.add_parser(
        'express',
        prog='lib5c express',
        help='express normalization',
        parents=[primerfile_parser, level_parser, simple_in_out_parser,
                 parallelization_parser]
    )
    express_parser.add_argument(
        '-J', '--joint_normalize',
        action='store_true',
        help='''Normalize all input files using a single shared bias vector.''')
    express_parser.add_argument(
        '-B', '--output_bias',
        action='store_true',
        help='''If this flag is present, the bias vectors will be written to
        .bias files located next to the output .counts files.''')
    express_parser.add_argument(
        '-e', '--epsilon',
        type=float,
        default=1e-4,
        help='''The relative improvement in the residual before declaring
        convergence. The default is 1e-4.''')
    express_parser.add_argument(
        '-i', '--max_iterations',
        type=int,
        default=3000,
        help='''Maximum number of iterations. The default is 3000.''')
    express_parser.add_argument(
        '-o', '--plot_outfile',
        type=str,
        help='''Pass a string reference to a path to which to write
        visualizations of the residual as a function of number of iterations.
        This string should include one %%r, which will be replaced with the
        region name.''')
    express_parser.add_argument(
        '-m', '--expected_model', type=str, help='''Pass a string reference to a
        countsfile containing the expected model to be used for express
        balancing. If this is not passed, a linear log-log fit will be used.''')
    express_parser.set_defaults(func=express_tool)


def express_tool(parser, args):
    import os
    import glob

    import numpy as np

    from lib5c.tools.helpers import resolve_level, resolve_parallel, \
        infer_replicate_names, resolve_primerfile, resolve_expected_models
    from lib5c.algorithms.express import express_normalize_matrix, \
        joint_express_normalize
    from lib5c.algorithms.expected import \
        make_poly_log_log_binned_expected_matrix, \
        make_poly_log_log_fragment_expected_matrix
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    from lib5c.writers.counts import write_counts
    from lib5c.writers.bias import write_cis_bias_vector
    from lib5c.util.system import check_outdir

    # resolve primerfile and parallel
    primerfile = resolve_primerfile(args.infile, args.primerfile)
    if not args.joint_normalize:
        resolve_parallel(parser, args, subcommand='express')

    # load counts
    print('loading counts')
    primermap = load_primermap(primerfile)
    if not args.joint_normalize:
        observed_counts = load_counts(args.infile, primermap)
    else:
        infiles = glob.glob(args.infile)
        observed_counts = [load_counts(infile, primermap) for infile in infiles]

    # resolve expected model
    if not args.joint_normalize:
        if args.expected_model is not None:
            print('loading expected model from %s' % args.expected_model)
            expected_counts = load_counts(args.expected_model, primermap)
        else:
            print('precomputing expected model')
            if resolve_level(primermap, args.level) == 'fragment':
                expected_counts = make_poly_log_log_fragment_expected_matrix(
                    observed_counts, primermap)
            else:
                expected_counts = make_poly_log_log_binned_expected_matrix(
                    observed_counts)
    else:
        expected_counts = resolve_expected_models(
            args.expected_model, observed_counts, primermap, level=args.level)

    # express normalize
    if not args.joint_normalize:
        print('express normalizing')
        balanced_counts, bias_factors, errs = express_normalize_matrix(
            observed_counts, expected_counts, max_iter=args.max_iterations,
            eps=args.epsilon)
    else:
        print('joint express normalizing')
        # deduce regions
        regions = observed_counts[0].keys()

        # reshape
        reshaped_observed_counts = {
            region: [observed_counts[i][region]
                     for i in range(len(observed_counts))]
            for region in regions}
        reshaped_expected_counts = {
            region: [expected_counts[i][region]
                     for i in range(len(observed_counts))]
            for region in regions}

        # joint normalize
        raw_balanced_counts, bias_factors, errs = joint_express_normalize(
            reshaped_observed_counts, reshaped_expected_counts,
            max_iter=args.max_iterations, eps=args.epsilon)

        # reshape
        balanced_counts = [{region: raw_balanced_counts[region][i]
                            for region in regions}
                           for i in range(len(observed_counts))]

    # plot error
    if args.plot_outfile:
        print('plotting output')
        for region in errs.keys():
            resolved_outfile = args.plot_outfile.replace(r'%r', region)
            check_outdir(resolved_outfile)
            import matplotlib.pyplot as plt
            plt.clf()
            plt.plot(range(1, len(errs[region])), np.log(errs[region][1:]))
            plt.title('%s convergence' % region)
            plt.ylabel('log(L1 error)')
            plt.xlabel('iteration number')
            plt.savefig(resolved_outfile)

    # write counts
    print('writing counts')
    if not args.joint_normalize:
        write_counts(balanced_counts, args.outfile, primermap)
        if args.output_bias:
            biasfile = '%s.bias' % os.path.splitext(args.outfile)[0]
            print('writing bias vector')
            write_cis_bias_vector(bias_factors, primermap, biasfile)
    else:
        replicate_names = infer_replicate_names(
            infiles, pattern=args.infile if '*' in args.infile else None)
        outfiles = [args.outfile.replace(r'%s', rep) for rep in replicate_names]
        for i in range(len(balanced_counts)):
            write_counts(balanced_counts[i], outfiles[i], primermap)
        if args.output_bias:
            print('writing bias vectors')
            for i in range(len(balanced_counts)):
                biasfile = '%s.bias' % os.path.splitext(outfiles[i])[0]
                write_cis_bias_vector(bias_factors, primermap, biasfile)
