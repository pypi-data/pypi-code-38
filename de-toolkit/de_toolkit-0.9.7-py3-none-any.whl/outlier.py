r'''
Usage:
    detk-outlier entropy <counts_fn> [options]
    detk-outlier shrink [options] <counts_fn>
'''
TODO = '''
    detk-outlier trim [options] <counts_fn>
'''

cmd_opts = {
    'entropy':r'''
Usage:
    detk-outlier entropy <counts_fn> [options]

Options:
    -p P --percentile=P    Float value between 0 and 1
    -o FILE --output=FILE  Name of the ouput csv
    --plot-output=FILE     Name of the plot png
''',
    'shrink':r'''
Usage:
    detk-outlier shrink [options] <counts_fn>

Options:
    -o FILE --output=FILE   Destination of primary output [default: stdout]
    -f N --shrink-factor=N  Shrinkage factor number float between 0 and 1 [default: 0.25]
    -p N --p-max=N          Percent counts of sample default is sqrt(1/num samples)
    -i N --iters=N          Number of terations [default: 1000]
''',
}

import csv, os
from docopt import docopt
import logging
import matplotlib as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pprint import pformat
import scipy.stats as sc
import sys

from .common import CountMatrixFile, DetkModule, _cli_doc, make_cli_count_obj, set_logging, write_output
from .report import DetkReport
from .util import stub

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def pmf_transform(count_obj, shrink_factor=0.25, p_max=None, iters=1000):
    obj = PMFTransform(count_obj, shrink_factor, p_max, iters)
    return obj.output

class PMFTransform(DetkModule):
    def __init__(self, count_obj, shrink_factor=0.25, p_max=None, iters=1000):
        self['params'] = {
                'shrink_factor': shrink_factor,
                'p_max': p_max,
                'iters': iters
                }
        count_obj = count_obj.copy()
        p_max = p_max or np.sqrt(1./len(count_obj))

        for i in range(iters) :
            p_count = count_obj/count_obj.sum()

            if count_obj.sum() == 0 :
                print('all samples set to zero, returning')
                break

            p_count_outliers = p_count>p_max

            if not p_count_outliers.any() :
                break # done

            max_non_outliers = max(count_obj[~p_count_outliers])

            count_obj[p_count_outliers] = max_non_outliers+(count_obj[p_count_outliers]-max_non_outliers)*shrink_factor
#        if i == iters :
#            print('PMF transform did not converge')
#            print(p_x)
#            print(p_x_outliers)
        
        self.count_obj = count_obj

    @property
    def output(self):
        return self.count_obj

    @property
    def properties(self):
        return {'num_kept':len(self.count_obj)}

def shrink(count_obj, shrink_factor=0.25, p_max=None, iters=1000) :
    '''
    Outlier count shrinkage routine as described in Labadorf et al, PLOSONE (2015)

    This algorithm identifies feature where a small number of samples contains a
    disproportionately large number of the overall counts for that feature
    across samples. For each feature the algorithm is as follows:

    1. Divide each sample count by the sum of counts (i.e. sample count
       proportions)

    2. Identify samples that have >*p_max* sample count proportion

        a. If no samples are identified, return the most recent set of adjusted
           counts

        b. Else, shrink the identified samples toward the largest sample *s* for
           which P(x)<*p_max* by multiplying the difference between the
           outlier sample and *s* by the shrinkage factor and replacing
           *o* with *s* the shrunken count value

    3. Go to 1, repeat until no samples exceed *p_max* count proportion

    This strategy assumes that samples with disproportionate count contribution
    are outliers and that the order of samples is correct and the magnitude is
    sometimes not. The order of the samples is thus always maintained, and the
    shrinking does not introduce new false positives beyond what would already
    be in the dataset. The maximum proportion of reads allowed in one sample,
    p, and the shrinkage factor were both set to 0.2.

    Parameters
    ----------
    count_obj: de_toolkit.CountMatrix object
        counts object
    shrink_factor: float
        number between 0 and 1 that determines how much the residual counts of
        outlier samples is shrunk in each iteration
    p_max: float
        number between 0 and 1 that indicates the maximum proportion of counts
        a sample may have before being considered an outlier, default is
        ``sqrt(1/num_samples)``
    '''
    obj = ShrinkCounts(count_obj, shrink_factor, p_max, iters)
    return obj.output

class ShrinkCounts(DetkModule):
    def __init__(self, count_obj, shrink_factor=0.25, p_max=None, iters=1000):
        self['params'] = {
                'shrink_factor': shrink_factor,
                'p_max': p_max,
                'iters': iters
                }
        logger.info('PMF shrink params: %s',pformat(self['params']))
        shrunk_counts = count_obj.counts.apply(
            pmf_transform,
            shrink_factor=shrink_factor,
            p_max=p_max,
            iters=iters
        )
        shrunk_counts = pd.DataFrame(
                shrunk_counts,
                index=count_obj.counts.index,
                columns=count_obj.counts.columns
            )

        logger.info('counts removed by shrinking: %.2f',shrunk_counts.sum().sum()-count_obj.counts.sum().sum())
        self.shrunk_counts = shrunk_counts

        logger.info('PMF shrink done')

    @property
    def output(self):
        return self.shrunk_counts

    @property
    def properties(self):
        return {'num_kept': len(self.shrunk_counts)}

@stub
def trim(count_obj) :
    '''
    possibly implement some trimmed-mean trimming
    '''
    pass

def entropy(counts_obj, threshold):
    '''
    Calculate sample entropy for each gene and flag genes that exceed the lower
    threshold'ile

    Sample entropy is a metric that can be used to identify outlier samples by
    locating rows which are overly influenced by a single count value. This
    metric is calculated for each gene/feature *g* as follows::

        p_i = c_i/sumj(c_j)
        sum(p_i) = 1
        H_g = -sum_i(p_i*log2(p_i))

    Here, c_i is the number of counts in sample i, p_i is the fraction of reads
    contributed by sample i to the overall counts of the row, and H_g is the
    Shannon entropy of the row when using log2. The maximum value possible for
    H is 2 when using Shannon entropy. Genes/features with very low entropy are
    those where a small number of samples makes up most of the counts across
    all samples.

    Parameters
    ----------
    counts_obj: de_toolkit.CountMatrix
        count matrix object
    threshold: float
        the lower percentile below which to flag genes

    Returns
    -------
    pandas.DataFrame
        data frame with one row for each row in the input counts matrix and two
        columns:
        
        - *entropy*: the calculated entropy value for that row
        - *entropy_p0_XX*: a True/False column for genes flagged as having an
          entropy value less than the 0.XX percentile; *XX* is the
          first two digits of the selected threshold
    '''
    obj = EntropyCounts(counts_obj, threshold)
    return obj.output


class EntropyCounts(DetkModule):
    def __init__(self, counts_obj, threshold):
        self['params'] = {'threshold': threshold}
        self.counts_obj = counts_obj
        logger.info('entropy thresholding')

        counts_transpose = counts_obj.counts.copy().transpose()
        trshld_name = str(threshold).split('.')[1]

        # check that no features have a total of zero
        all_features = counts_transpose.columns.tolist()
        counts_transpose = counts_transpose.loc[:, (counts_transpose != 0).any(axis=0)]
        nonzero_features = counts_transpose.columns.tolist()
        dropped_features = set(all_features) - set(nonzero_features)

        # create a null results df for all of the dropped features
        dropped_df = pd.DataFrame(columns=['entropy', 'entropy_p0_{}'.format(trshld_name)], index=dropped_features)
        dropped_df.replace(dropped_df, 'Null')

        # calculate the entropy over all of the features
        entropy = counts_transpose.apply(func=sc.entropy, axis=0)

        # gathers the features and entropy values for the respective quantile groups
        entropy_threshold = np.percentile(entropy, q=threshold)

        # create the results of the entropy test
        # column 1 is the entropy value
        # column 2 is a boolean indication whether the value is under the user described threshold
        results_df = pd.DataFrame(entropy, columns=['entropy'])
        results_df['entropy_p0_{}'.format(trshld_name)] = entropy < entropy_threshold
        logger.info('number of flagged features: %d',(entropy<entropy_threshold).sum())

        frames = [results_df, dropped_df]
        results_df = pd.concat(frames)
        # set the results index to be in the same order as the counts index
        results_df.index = counts_obj.counts.index

        self.results_df = results_df
        logger.info('entropy threshold done')

    @property
    def output(self):
        return self.results_df

    @property
    def properties(self):
        return {'num_kept': len(self.results_df)
                }


def plot_entropy(entropy_res, threshold, name=None, show=None):
    '''
    Function accepts a counts file, a cutoff threshold. The counts file should have the samples
    as the columns and the features as the rows. The cutoff threshold should be a float value
    between 0 and 1. If a name (in the the form of *.png) is given, the figure will be saved with
    the specified name. If show is set to 'show', the plot will be shown.
    '''

    entropy = entropy_res['entropy']

    # sort the entropy values in ascending order
    entropy = entropy.sort_values(ascending=True)
    entropy_threshold = np.percentile(entropy, q=threshold)

    # plot histogram
    fig = plt.gcf()
    plt.hist(entropy, bins='auto', log=True)
    plt.axvline(entropy_threshold, color='red')
    plt.xlabel('Entropy')
    plt.ylabel('Samples Per Bin')
    plt.title('Binned Feature Entropy')
    plt.legend(['P < {}'.format(threshold), 'Data'])
    fig.set_size_inches(10,10)

    if name == None and show != None:
        plot.show()
    elif name != None:
        fig.savefig(name, dpi=100)
    elif name != None and show != None:
        fig.savefig(name, dpi=100)
        plot.show()

def main(argv=sys.argv):

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    # add the common opts to the docopt strings
    cmd_opts_aug = {}
    for k,v in cmd_opts.items() :
        cmd_opts_aug[k] = _cli_doc(v)

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts) :
        docopt(_cli_doc(__doc__),argv)
    argv = argv[1:]
    cmd = argv[0]

    if cmd == 'entropy' :
        args = docopt(cmd_opts_aug['entropy'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        count_obj = make_cli_count_obj(args)
        pval = float(args['--percentile'])

        # run the entropy_calc function
        try :
            out = EntropyCounts(count_obj.counts, pval)
        except Exception as e :
            logger.error(e)
            sys.exit(1)

        if args['--plot-output'] :
            logger.info('plotting entropy threshold to %s',args['--plot-output'])
            plot_entropy(out_df, pval, name=plot)

    elif cmd == 'trim' :
        args = docopt(cmd_opts_aug['trim'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        count_obj = CountMatrixFile(args['<counts_fn>'])
        out = trim(count_obj)

    elif cmd == 'shrink' :
        args = docopt(cmd_opts_aug['shrink'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        count_obj = CountMatrixFile(args['<counts_fn>'])
        if args['--p-max'] is None:
            args['--p-max'] = np.sqrt(1./count_obj.counts.shape[1])

        try :
            out = ShrinkCounts(count_obj,
                    shrink_factor=float(args['--shrink-factor']),
                    p_max=float(args['--p-max']),
                    iters=int(args['--iters'])
                )
        except Exception as e :
            logger.error(e)
            sys.exit(1)

    write_output(out.output,args)

    # write out the report json
    if not args['--no-report'] :
        logging.info('writing report to %s',args['--report-dir'])
        with DetkReport(args['--report-dir']) as r :
            r.add_module(
                    out,
                    in_file_path=args['<counts_fn>'],
                    out_file_path=args['--output'],
                    column_data_path=args.get('--column-data'),
                    workdir=os.getcwd()
                    )
    else :
        logging.info('not generating report due to --no-report')

    logging.info('done')

if __name__ == '__main__':
    main()
