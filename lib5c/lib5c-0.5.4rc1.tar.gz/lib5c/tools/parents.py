import argparse

primerfile_parser = argparse.ArgumentParser(add_help=False)
primerfile_parser.add_argument(
    '-p', '--primerfile',
    type=str,
    help='''Primer file or bin file to use. If this flag is not present, a .bed
    file will be searched for based on the locations of the input files.'''
)

level_parser = argparse.ArgumentParser(add_help=False)
level_parser.add_argument(
    '-l', '--level',
    type=str,
    choices=['bin', 'fragment', 'auto'],
    default='auto',
    help='''Specify whether the input files should be interpreted as fragment
    level or bin level. The default is 'auto', which guesses the apporpriate
    level based on the content of the primerfile.'''
)

simple_in_out_parser = argparse.ArgumentParser(add_help=False)
simple_in_out_parser.add_argument(
    'infile',
    type=str,
    help='''Input countsfile.''')
simple_in_out_parser.add_argument(
    'outfile',
    type=str,
    help='''Output countsfile.''')

filter_parser = argparse.ArgumentParser(add_help=False)
filter_parser.add_argument(
    '-w', '--window_width',
    type=int,
    default=20000,
    help='''The width of the window to use to bin counts, in base pairs. The
    default is 20000.''')
filter_parser.add_argument(
    '-f', '--function',
    type=str,
    default='gmean',
    choices=['sum', 'median', 'amean', 'gmean'],
    help='''The function to apply to fragment-level counts that fall within
    the binning window. Default is 'gmean'.''')
filter_parser.add_argument(
    '-W', '--wipe_unsmoothable_columns',
    action='store_true',
    help='''Pass this flag to set all "unsmoothable columns" to nan.''')
filter_parser.add_argument(
    '-M', '--midpoint',
    action='store_true',
    help='''Pass this flag to use the fragment midpoint when computing distances
    to fragments. This does not affect bin-bin smoothing.''')
filter_parser.add_argument(
    '-I', '--inverse',
    action='store_true',
    help='''Pass this flag to apply an inversely proportional weight 1/(d+1)
    where d is the distance in bin index space as determined by a p-norm of
    order 1 unless overriden by -n/--norm_order.''')
filter_parser.add_argument(
    '-G', '--gaussian',
    action='store_true',
    help='''Pass this flag to apply a Gaussian weight to the function
    specified by the -f/--function flag. This has no effect on the 'median'
    and 'sum' functions. By default, this Gaussian will have standard
    deviation equal to the width specified in the -w/--window_width flag,
    but this can be overriden by the -s/--sigma flag. Also by default, this
    will evaluate the Gaussian using the L1 norm in genomic interaction
    space, but this can be overriden by the -n/--norm flag.''')
filter_parser.add_argument(
    '-s', '--sigma',
    type=int,
    help='''The standard deviation of the Gaussian to use for weighting.
    This flag has no effect if the -G/--gaussian flag is not present. The
    default is the window width.''')
filter_parser.add_argument(
    '-n', '--norm_order',
    type=int,
    help='''Order of the p-norm in genomic interaction space that will be
    used to evaluate weight functions. This flag has no effect if no weight
    function is invoked, i.e., when neither -G/--gaussian nor -I/--inverse
    is present. The default is 1.''')
filter_parser.add_argument(
    '-t', '--threshold',
    type=float,
    default=0.0,
    help='''If the fraction of possible fragment-level interactions falling
    within a bin's window that are positive is less than or equal to this
    value, the bin will be considered too sparse to draw conclusions from
    and it will be assigned nan. The default is 0.0.''')

parallelization_parser = argparse.ArgumentParser(add_help=False)
parallelization_parser.add_argument(
    '-H', '--hang',
    action='store_true',
    help='''If multiple input files are specified, this flag will cause the
    terminal to hang until all input files have finished processing.''')

region_parser = argparse.ArgumentParser(add_help=False)
region_parser.add_argument(
    '-r', '--region',
    type=str,
    help='''Region to generate output for. If this flag is omitted all
    regions will be processed. If processing all regions, include a %%r in
    the outfile, which will be replaced with the region name.''')

distribution_parser = argparse.ArgumentParser(add_help=False)
distribution_parser.add_argument(
    '-m', '--mode',
    type=str,
    choices=['log_log_fit', 'obs_over_exp', 'regional_simple',
             'regional_shifted'],
    default='obs_over_exp',
    help='''This flag determines what method will be used to estimate the
    variance scaling factor. The default is 'obs_over_exp'. See the README
    for more details.''')
distribution_parser.add_argument(
    '-d', '--distribution',
    type=str,
    default='nbinom',
    help='''The distribution to use to evaluate the p-values. This must be a
    subclass of scipy.stats.rv_discrete or scipy.stats.rv_continuous. If it
    is a subclass of rv_discrete, approaches that depend on MLE fits may be
    unavailable. The default is 'nbinom'.''')
distribution_parser.add_argument(
    '-L', '--log',
    action='store_true',
    help='''Pass this flag to treat the distribution specified by the
    -d/--distribution flag as modeling the counts in log space.''')

donut_parser = argparse.ArgumentParser(add_help=False)
donut_parser.add_argument(
    '-D', '--donut',
    action='store_true',
    help='''Pass this flag to use a local donut selector (local variance
    estimator).''')
donut_parser.add_argument(
    '-v', '--donut_inner_size',
    type=int,
    default=5,
    help='''The inner size of the donut to use. The default is 5.''')
donut_parser.add_argument(
    '-w', '--donut_outer_size',
    type=int,
    default=15,
    help='''The outer size of the donut to use. The default is 15.''')

expected_selection_parser = argparse.ArgumentParser(add_help=False)
expected_selection_parser.add_argument(
    '-n', '--num_groups',
    type=int,
    default=100,
    help='''The number of groups of points with similar expected values to
    select. The default is 100.''')
expected_selection_parser.add_argument(
    '-f', '--group_fractional_tolerance',
    type=float,
    default=0.1,
    help='''Points whose expected value is within this fractional tolerance of
    the group center will be included in the group. The default is 0.1.''')
expected_selection_parser.add_argument(
    '-e', '--exclude_offdiagonals',
    type=int,
    default=5,
    help='''Exclude this many off-diagonals when selecting by expected. Pass 0
    to exclude only the exact diagonal. Pass -1 to exclude nothing. Default is
    5.''')

log_vs_vst_parser = argparse.ArgumentParser(add_help=False)
log_vs_vst_group = log_vs_vst_parser.add_mutually_exclusive_group()
log_vs_vst_group.add_argument(
    '-L', '--log',
    action='store_true',
    help='''Pass this flag to log observed values, expected values, and variance
    estimates (if applicable).''')
log_vs_vst_group.add_argument(
    '-V', '--vst',
    action='store_true',
    help='''Pass this flag to log the expected values only.''')

lim_parser = argparse.ArgumentParser(add_help=False)
lim_parser.add_argument(
    '-x', '--xlim',
    type=str,
    help='''Pass a tuple '(min,max)' to force the x-limits of the plot.''')
lim_parser.add_argument(
    '-y', '--ylim',
    type=str,
    help='''Pass a tuple '(min,max)' to force the y-limits of the plot.''')

var_parser = argparse.ArgumentParser(add_help=False)
var_parser.add_argument(
    '--rep',
    type=str,
    help='''If -s/--source involves 'cross_rep', pass a rep name to specify
    which of the input reps to compute variance estimates for.''')
var_parser.add_argument(
    '-m', '--model',
    type=str,
    choices=['norm', 'lognorm', 'loglogistic', 'nbinom', 'poisson'],
    default='lognorm',
    help='''Statistical model to use. Default is 'lognorm'.''')
var_parser.add_argument(
    '-s', '--source',
    type=str,
    choices=['local', 'cross_rep', 'deviation', 'mle',
             'cross_rep_plus_deviation'],
    default='deviation',
    help='''Variance source to use. If 'mle', no trend fitting is performed.
    If 'cross_rep', observed must be a glob-expandable file pattern matching
    observed countsfiles for multiple replicates (quoted to prevent shell
    expansion), and automatic parallelization across replicates will be
    disabled. Default is 'deviation'.''')
var_parser.add_argument(
    '-f', '--fitter',
    type=str,
    choices=['lowess', 'group', 'constant', 'none'],
    default='lowess',
    help='''Fitter to use to fit the variance trend. Default is 'lowess'.''')
var_parser.add_argument(
    '-a', '--agg_fn',
    type=str,
    choices=['median', 'mean', 'lowess'],
    default='lowess',
    help='''Aggregation function to use when -f/--fitter is 'group' or
    'constant'. Has no effect otherwise. Default is 'lowess'.''')
var_parser.add_argument(
    '--min_obs',
    type=float,
    default=2.0,
    help='''Points with observed values below this threshold in any replicate
    will be excluded. Default is 2.0.''')
var_parser.add_argument(
    '--min_disp',
    type=str,
    default='1e-8',
    help='''Forces the minimum value of the dispersion value. Default is
    1e-8.''')
var_parser.add_argument(
    '--min_dist',
    type=int,
    default=6,
    help='''Points with interaction distances (in bin units) below this
    threshold in any replicate will be excluded. Default is 6.''')
