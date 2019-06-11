r'''
Easy access to informative count matrix statistics. Each of these functions
produces two outputs:

- a json formatted file containing relevant statistics in a machine-parsable
  format
- an optional human-friendly HTML page displaying the results

All of the commands accept a single counts file as input with optional
arguments as indicated in the documentation. By default, the JSON and HTML
output files have the same basename without extension as the counts file but
including .json or .html as appropriate. E.g., counts.csv will produce
counts.json and counts.html in the current directory. These default filenames
can be changed using optional command line arguments --json=<json fn> and
--html=<html fn> as appropriate for all commands. If <json fn>, either default
or specified, already exists, it is read in, parsed, and added to. The HTML
report is overwritten on every invocation using the contents of the JSON file.

Some subcommands have specialize options. Examine the help messages for each
command individually to view, e.g. detk-stats summary -h.

Usage:
    detk-stats summary [options] <counts_fn> [<cov_fn>]
    detk-stats basestats [options] <counts_fn>
    detk-stats coldist [options] <counts_fn>
    detk-stats rowdist [options] <counts_fn>
    detk-stats colzero [options] <counts_fn>
    detk-stats rowzero [options] <counts_fn>
    detk-stats entropy [options] <counts_fn>
    detk-stats pca [options] <counts_fn> [<cov_fn>]

Common Stats Options:
    -h --help              Access detailed help for individual commands
    -o FILE --output FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
'''

cmd_opts = {
    'summary':r'''
Compute summary statistics on a counts matrix file.

This is equivalent to running each of these tools separately:

- basestats
- coldist
- colzero
- rowzero
- entropy
- pca

Usage:
    detk-stats summary [options] <counts_fn> [<cov_fn>]

Options:
    -h --help
    --column-data=FN       DEPRECATED: pass cov_fn as positional command line
                           argument instead
    --color-col=COLNAME    Use column data column COLNAME for coloring output plots
    --bins=BINS            Number of bins to use for the calculated
                           distributions [default: 20]
    --log                  log transform count statistics
    --density              Produce density distribution by dividing each distribution
                           by the appropriate sum
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'basestats':r'''
Calculate basic statistics of the counts file, including:
    number of samples
    number of rows

Usage:
    detk-stats basestats [options] <counts_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'coldist':r'''
Column-wise distribution of counts

Compute the distribution of counts column-wise. Each column is subject to
binning by percentile, with output identical to that produced by np.histogram.

In the stats object, the fields are defined as follows:
    pct
        The percentiles of the distributions in the range 0 < pct < 100, by
        default in increments of 5. This defines the length of the dist and
        bins arrays in each of the objects for each sample.
    dists
        Array of objects containing one object for each column, described below.
    Each item of dists is an object with the following keys:
        name
            Column name from original file
        dist
            Array of raw or normalized counts in each bin according to the
            percentiles from pct
        bins
            Array of the bin boundary values for the distribution. Should
            be of length len(counts)+1. These are what would be the x-axis
            labels if this was plotted as a histogram.
        extrema
            Object with two keys, min and max, that contain the literal
            count values for counts that have a value larger or smaller than
            1.5*(inner quartile length) of the distribution. These could be
            marked as outliers in a boxplot, for example.

Usage:
    detk-stats coldist [options] <counts_fn>

Options:
    --bins=N               The number of bins to use when computing the counts
                           distribution [default: 20]
    --log                  Perform a log10 transform on the counts before
                           calculating the distribution. Zeros are omitted
                           prior to histogram calculation.
    --density              Return a density distribution instead of counts,
                           such that the sum of values in *dist* for each
                           column approximately sum to 1.
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'rowdist':r'''
Row-wise distribution of counts

Compute the distribution of counts row-wise. Each row is subject to binning by
percentile, with output identical to that produced by np.histogram.

In the stats object, the fields are defined as follows:
    pct
        The percentiles of the distributions in the range 0 < pct < 100, by
        default in increments of 5. This defines the length of the dist and
        bins arrays in each of the objects for each sample.
    dists
        Array of objects containing one object for each column, described
        below.
    Each item of dists is an object with the following keys:
        name
            Column name from original file
        dist
            Array of raw or normalized counts in each bin according to the
            percentiles from pct
        bins
            Array of the bin boundary values for the distribution. Should
            be of length len(counts)+1. These are what would be the x-axis
            labels if this was plotted as a histogram.
        extrema
            Object with two keys, min and max, that contain the literal
            count values for counts that have a value larger or smaller than
            1.5*(inner quartile length) of the distribution. These could be
            marked as outliers in a boxplot, for example.

Usage:
    detk-stats rowdist [options] <counts_fn>

Options:
    --bins=N               The number of bins to use when computing the counts
                           distribution [default: 20]
    --log                  Perform a log10 transform on the counts before calculating
                           the distribution. Zeros are omitted prior to histogram
                           calculation.
    --density              Return a density distribution instead of counts, such that
                           the sum of values in *dist* for each row approximately
                           sum to 1.
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'colzero':r'''
Column-wise distribution of zero counts

Compute the number and fraction of exact zero counts for each column.
The stats value is an array containing one object per column as follows:
    name
        column name
    zero_count
        absolute count of rows with exactly zero counts
    zero_frac
        zero_count divided by the number of rows
    col_mean
        the mean of counts in the column
    nonzero_col_mean
        the mean of only the non-zero counts in the column

Usage:
    detk-stats colzero [options] <counts_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
            ''',
    'rowzero':r'''
Row-wise distribution of zero counts

Compute the number and fraction of exact zero counts for each row.
The stats value is an array containing one object per row as follows:
    name
        row name
    zero_count
        absolute count of rows with exactly zero counts
    zero_frac
        zero_count divided by the number of rows
    row_mean
        the mean of counts in the row
    nonzero_row_mean
        the mean of only the non-zero counts in the row

Usage:
    detk-stats rowzero [options] <counts_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'entropy':r'''
Row-wise sample entropy calculation

Sample entropy is a metric that can be used to identify outlier samples by locating
rows which are overly influenced by a single count value. This metric can be
calculated for a single row as follows:
    pi = ci/sumj(cj)
    sum(pi) = 1
    H = -sumi(pi*log2(pi))
Here, ci is the number of counts in sample i, pi is the fraction of reads contributed
by sample i to the overall counts of the row, and H is the Shannon entropy of the row
when using log2. The maximum value possible for H is 2 when using Shannon entropy.

Rows with a very low H indicate a row has most of its count mass contained in a small
number of columns. These are rows that are likely to drive outliers in downstream
analysis, e.g. differential expression.

The key entropies is an array containing one object per row with the following keys:
    name
        row name from counts file
    entropy
        the value of H calculated as above for that row

Usage:
    detk-stats [options] entropy <counts_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
''',
    'pca':r'''
Principal common analysis of the counts matrix.

This module performs PCA on a provided counts matrix and returns the principal
component weights, scores, and variances. In addition, the weights and scores
for each individual component can be combined to define the projection of each
sample along that component.

The PCA module can also accept a metadata file that contains information about
the samples in each column. The user can specify some of these columns to
include as variables for plotting purposes. The idea is that columns labeled
with the same class will be colored according to their class, such that
separations in the data can be more easily observed when projections are
plotted.

Usage:
    detk-stats pca [options] <counts_fn> [<cov_fn>]

Options:
    --column-data=FN       DEPRECATED: pass cov_fn as positional command line
                           argument instead
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    -f FMT --format=FMT    Format of output, either csv or table [default: csv]
'''
}
from collections import OrderedDict, defaultdict
import csv
from docopt import docopt
import json
import logging
from pprint import pformat
import math
import numpy as np
import pandas
import pkg_resources
import os.path
import scipy
from sklearn.decomposition import PCA
from string import Template
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
import sys
import warnings

from .common import (CountMatrixFile, DetkModule, _cli_doc, set_logging,
        make_cli_count_obj, write_output)
from .report import DetkReport

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def summary(count_mat,
        bins=20,
        log=False,
        density=False) :
    '''
    Compute summary statistics on a counts matrix file.

    This is equivalent to running each of these tools separately:

    - basestats
    - coldist
    - colzero
    - rowzero
    - entropy
    - pca

    Parameters
    ----------
    count_mat : CountMatrix object
        count matrix object
    bins : int
        number of bins, passed to coldist
    log : bool
        perform log10 transform of counts in coldist
    density : bool
        return a density distribution from coldist

    Returns
    -------
    list
        list of DetkModule subclasses for each of the called submodules
    '''

    total_output = [
        BaseStats(count_mat),
        ColDist(count_mat, bins, log, density),
        #RowDist(count_mat, bins, log, density),
        ColZero(count_mat),
        RowZero(count_mat),
        Entropy(count_mat),
        CountPCA(count_mat)
    ]

    return total_output

class BaseStats(DetkModule) :
    '''
        Basic statistics of the counts file

        The most basic statistics of the counts file, including:
        - number of columns
        - number of rows

    '''
    def __init__(self, count_mat) :

        self.count_mat = count_mat

    @property
    def properties(self):
        #Get counts, number of columns, and number of rows
        return {
                'num_rows': self.count_mat.counts.shape[0],
                'num_cols': self.count_mat.counts.shape[1]
               }

    @property
    def output(self):
        '''
        Example output output::

            +basestats-+-----+
            | stat     | val |
            +----------+-----+
            | num_cols | 4   |
            | num_rows | 3   |
            +----------+-----+
        '''
        return [
                ['stat','val'],
                ['num_cols',self.properties['num_cols']],
                ['num_rows',self.properties['num_rows']]
               ]

class ColDist(DetkModule) :
    '''
        Column-wise distribution of counts

        Compute the distribution of counts column-wise. Each column is subject
        to binning by percentile, with output identical to that produced by
        np.histogram.

        Parameters
        ----------
        count_mat : CountMatrix
            count matrix containing counts
        bins : int
            number of bins to use when computing distribution
        log : bool
            take the log10 of counts+1 prior to computing distribution
        density : bool
            return densities rather than absolute bin counts for the
            distribution, densities sum to 1

    '''
    def __init__(self,count_mat,bins=100,log=False,density=False):

        self['params'] = {
                'bins': bins,
                'log': log,
                'density': density
        }

        self['pct'] = pct = np.arange(bins)/bins

        self['dists'] = []

        self.stats = stats = OrderedDict()

        for col in count_mat.counts:

            #to access the data in each column
            data = count_mat.counts[col]

            #Take the log10 of each count if log option is specified
            if log :
                data = np.log10(data+1)

            #for the histogram bin edges and count numbers
            n, dist_bins = np.histogram(data,bins=bins,density=density)

            binstart=dist_bins[:-1]
            bincount=n
            pctVal=np.percentile(data,100*pct)

            stats[col] = OrderedDict(
                binstart=binstart,
                bincount=bincount,
                pct=pct,
                pctVal=pctVal
            )

            # unlog binstarts and pctVals
            if log :
                binstart = 10**binstart
                pctVal = 10**pctVal

            #make the dict for each sample
            self['dists'].append(
                {
                    'name':col,
                    'dist':list(zip(binstart,bincount)),
                    'percentiles':list(zip(pct,pctVal))
                }
            )

    @property
    def output(self) :
        '''
        Tabular output is a table with four columns per input counts column:

          - bin start value (column name: sampleA__binstart)
          - number of features with counts or density in bin (sampleA__bincount)
          - percentile increment (i.e. 0, 1, etc) (sampleA__pct)
          - percentile value for corresponding percentile (sampleA__pctVal)

        '''
        res = []
        for col in self.stats :
            for colstat in self.stats[col] :
                res.append(['{}__{}'.format(col,colstat)]+list(self.stats[col][colstat]))
        return list(list(_) for _ in zip(*res))
    @property
    def properties(self) :
        '''
        In the properties object, the fields are defined as follows

        dists
            Array of objects containing one object for each column,
            described below.

        Each item of dists is an object with the following keys:

        name
            Column name from original file
        dist
            Array of (bin start, count) pairs defining the counts histogram
        percentile
            Array of (percentile, count) pairs defining the counts
            percentiles

        Example JSON properties output::

            {
              'dists' : [
                {
                  'name': 'H_0001',
                  'dist': [ [5, 129], [103, 317], ...],
                  'percentiles': [ [0, 193], [1, 362], ...],
                },
                {
                  'name': 'H_0002',
                  'dist': [ [6, 502], [122, 127], ...],
                  'bins': [ [0, 6000], [1, 6200], ...],
                }
              ]
            }
        '''
        return {
                'dists': self['dists']
               }

class RowDist(DetkModule):
    '''
        Row-wise distribution of counts

        Identical to coldist except calculated across rows. The name key is
        rowdist, and the name key of the items in dists is the row name from
        the counts file.

        Parameters
        ----------
        count_mat : CountMatrix
            count matrix containing counts
        bins : int
            number of bins to use when computing distribution
        log : bool
            take the log10 of counts prior to computing distribution
        density : bool
            return densities rather than absolute bin counts for the
            distribution, densities sum to 1
    '''
    def __init__(self, count_obj, bins=100, log=False, density=False) :

        self['params'] = {
                'bins': bins,
                'log': log,
                'density': density
        }

        self['pct'] = list(100*(_+1)/bins for _ in range(bins))
        self['dists'] = []

        for i in range(len(count_obj.feature_names)):
            #to access the data in each row
            data = count_obj.counts.iloc[i]

            #Compute log10 of each count if log option is specified
            if log :
                data = np.log10(data)

            #for the upper and lower outliers
            Q1 = np.percentile(data, 25)
            Q3 = np.percentile(data, 75)
            IQR =  np.percentile(data, 75) - np.percentile(data, 25)

            #for the histogram bin edges and count numbers
            n, dist_bins = np.histogram(data,bins=bins,density=density)

            #make the dict for each row
            self['dists'].append(
                    {
                        'name':count_obj.feature_names[i],
                        'dist':list(n),
                        'bins':list(dist_bins)[1:],
                        'extrema': {
                            'lower':[i for i in data if i < Q1-1.5*IQR],
                            'upper':[i for i in data if i > Q3+1.5*IQR]
                        }
                    }
                )
    @property
    def output(self) :
        '''
            Tabular output is a table where each row corresponds to a row
            with row name as the first column. The next columns are broken
            into two parts:

              - the bin start values, named like bin_N, where N is the
                percentile
              - the bin count values, named like dist_N, where N is the
                percentile
        '''
        colnames = ['rowname']+\
              ['bin_{}'.format(_) for _ in self['pct']]+\
              ['dist_{}'.format(_) for _ in self['pct']]
        res = [colnames]
        for dist in self['dists'] :
            res.append([dist['name']]+dist['bins']+dist['dist'])
        return res
    @property
    def properties(self) :
        '''Same format as ColDist'''
        return {
                'pct': self['pct'],
                'dists': self['dists']
               }

class ColZero(DetkModule) :
    '''
        Column-wise distribution of zero counts
    
        Compute the number and fraction of exact zero counts for each column.

    '''
    def __init__(self,count_mat) :
        #Get counts, number of columns, number of rows, and sample names
        num_rows, num_cols = count_mat.counts.shape
        col_names=count_mat.sample_names

        # Calculate zero counts, zero fractions, means, and nonzero means for
        # each column
        # the mean and median function raise warnings when a row/col is all zero
        # ignore
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            zero_counts = (count_mat.counts==0).sum(axis=0).fillna(0)
            zero_fracs = zero_counts/num_rows
            col_means = count_mat.counts.mean(axis=0)
            col_medians = count_mat.counts.median(axis=0)
            nonzero_col_means = count_mat.counts[count_mat.counts!=0].mean(axis=0)
            nonzero_col_medians = count_mat.counts[count_mat.counts!=0].median(axis=0)

        self['zeros'] = []

        for i in range(0, num_cols):
            col = {}
            col['name'] = col_names[i]
            col['zero_count'] = zero_counts[i]
            col['zero_frac'] = zero_fracs[i]
            col['mean'] = col_means[i]
            col['median'] = col_medians[i]
            col['nonzero_mean'] = nonzero_col_means[i]
            col['nonzero_median'] = nonzero_col_medians[i]
            self['zeros'].append(col)

    @property
    def output(self) :
        '''
            Tabular output is a table where each row corresponds to a column
            with the following fields:

            - name: Column name
            - zero_count: Number of zero counts
            - zero_frac: Fraction of zero counts
            - mean: Overall mean count
            - median: Overall median count
            - nonzero_mean: Mean of non-zero counts only
            - nonzero_median: Mean of non-zero counts only
        '''
        res = [['name','zero_count','zero_frac','mean','median','nonzero_mean','nonzero_median']]
        for col in self['zeros'] :
            res.append([col[_] for _ in res[0]])
        return res

    @property
    def properties(self):
        '''
        The stats value is an array containing one object per column as follows:

        name
            column name
        zero_count
            absolute count of rows with exactly zero counts
        zero_frac
            zero_count divided by the number of rows
        col_mean
            the mean of counts in the column
        col_median
            the median of counts in the column
        nonzero_col_mean
            the mean of only the non-zero counts in the column
        nonzero_col_median
            the median of only the non-zero counts in the column

        Example JSON output::

            {
              'zeros' : [
                {
                  'name': 'col1',
                  'zero_count': 20,
                  'zero_frac': 0.2,
                  'mean': 101.31,
                  'median': 31.31,
                  'nonzero_mean': 155.23,
                  'nonzero_median': 55.18
                },
                {
                  'name': 'col2',
                  'zero_count': 0,
                  'zero_frac': 0,
                  'mean': 3021.92,
                  'median': 329.23,
                  'nonzero_mean': 3021.92,
                  'nonzero_median': 819.32
                },
              ]
            }
        '''
        return { 'zeros':self['zeros'] }

class RowZero(DetkModule):
    '''
        Row-wise distribution of zero counts
    
        Computes statistics about the mean and median counts of rows by the
        number of zeros.
    '''
    def __init__(self,count_mat):

        #Get counts, number of columns, number of rows, and gene names
        cnts = count_mat.counts
        num_cols = cnts.shape[1]

        self['zeros'] = []

        num_zeros = (cnts==0).sum(axis=1)
        cum_frac = 0
        for i in range(0, num_cols+1) :
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                cnts_subset = cnts[num_zeros==i]
                frac = cnts_subset.shape[0]/cnts.shape[0]
                cum_frac += frac

                num_zero = {
                    'num_zeros': i,
                    'num_features': (num_zeros==i).sum(),
                    'feature_frac': frac,
                    'cum_feature_frac': cum_frac,
                    'mean': cnts_subset.mean(axis=1).fillna(0).mean(),
                    'nonzero_mean': cnts_subset[cnts_subset!=0].mean(axis=1).fillna(0).mean(),
                    'median': cnts_subset.median(axis=1).fillna(0).median(),
                    'nonzero_median': cnts_subset[cnts_subset!=0].median(axis=1).fillna(0).median()
                }

            self['zeros'].append(num_zero)

    @property
    def output(self) :
        '''
            Tabular output is a table where each row corresponds to rows
            having a given number of zero columns with the following fields:

              - num_zero: the number of zeros for this row
              - num_features: the number of features with this number of zeros
              - feature_frac: the fraction of features with this number of zeros
              - cum_feature_frac: cumulative fraction of features remeaning with
                this number of zeros or fewer
              - mean: the mean count mean of genes with this number of zeros
              - nonzero_mean: the mean count mean of genes with this number of
                zeros not including zero counts
              - median: the median count median of genes with this number of zeros
              - nonzero_median: the median count median of genes with this number
                of zeros, not including zero counts

        '''
        res = [['num_zeros','num_features','feature_frac','cum_feature_frac','mean','nonzero_mean','median','nonzero_median']]
        for col in self['zeros'] :
            res.append([col[_] for _ in res[0]])
        return res
    @property
    def properties(self) :
        '''
            The stats value is an array containing one object per number of zeros
            as follows:

            num_zero
                the number of zeros for this group of features
            num_features
                the number of features with this number of zeros
            feature_frac
                the fraction of features with this number of zeros
            cum_feature_frac
                cumulative fraction of features remeaning with this number of zeros
                or fewer
            mean
                the mean count mean of genes with this number of zeros
            nonzero_mean
                the mean count mean of genes with this number of zeros not
                including zero counts
            median
                the median count mean of genes with this number of zeros
            nonzero_median
                the median count mean of genes with this number of zeros, not
                including zero counts

            Example JSON output::

                {
                  'zeros' : [
                    {
                        'num_zeros': 0,
                        'num_features': 14031,
                        'feature_frac': .61,
                        'cum_feature_frac': .61,
                        'mean': 3351.13,
                        'nonzero_mean': 3351.13,
                        'median': 2125.9,
                        'nonzero_median': 2125.9
                    },
                    {
                        'num_zeros': 1,
                        'num_features': 5031,
                        'feature_frac': .21,
                        'cum_feature_frac': .82,
                        'mean': 3125.91,
                        'nonzero_mean': 3295.4,
                        'median': 1825.8,
                        'nonzero_median': 1976.1
                    },
                  ]
                }
        '''
        return { 'zeros':self['zeros'] }

class Entropy(DetkModule) :
    '''
    Row-wise sample entropy calculation

    Sample entropy is a metric that can be used to identify outlier samples
    by locating rows which are overly influenced by a small number of count
    values. This metric can be calculated for a single row as follows::

        pi = ci/sumj(cj)
        sum(pi) = 1
        H = -sumi(pi*log2(pi))

    Here, ci is the number of counts in sample i, pi is the fraction of
    reads contributed by sample i to the overall counts of the row, and H
    is the `Shannon entropy`_ of the row when using log2. The maximum value
    possible for H is 2 when using Shannon entropy.

    Rows with a very low H indicate a row has most of its count mass
    contained in a small number of columns. These are rows that are likely
    to drive outliers in downstream analysis, e.g. differential expression.

    .. _Shannon entropy: https://en.wikipedia.org/wiki/Entropy_(information_theory)
    '''
    def __init__(self,count_mat) :

        #Get counts, number of columns, number of rows, and gene names
        cnts = count_mat.counts.values
        num_cols=len(cnts[0])
        num_rows=len(cnts)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            entropies = count_mat.counts.apply(scipy.stats.entropy,axis=1)
            entropies[entropies.isnull()] = 0

        # there are 100 evenly spaced bins between [0,max_entropy]
        max_entropy = -np.log(1/num_cols)
        pct = list(range(100))
        pctVal = np.percentile(entropies,pct,interpolation='higher').tolist()

        #Format output
        self['entropies'] = res = defaultdict(list)
        res.update({
            'pct':pct,
            'pctVal':pctVal,
            #'entropies': entropies.tolist()
        })

        for p1, p2 in zip(pctVal,pctVal[1:]+[1e6]) :
            pct_features = entropies.index[(entropies>=p1) & (entropies<p2)]

            res['num_features'].append(pct_features.size)
            res['frac_features'].append(pct_features.size/entropies.size)
            res['cum_frac_features'].append(sum(res['frac_features']))

            if entropies[pct_features].size != 0 :
                min_feature = entropies[pct_features].idxmin()
                res['exemplar_features'].append({
                    'name': min_feature,
                    'entropy': entropies[min_feature],
                    'counts': list(zip(
                        count_mat.counts.columns,
                        count_mat.counts.loc[min_feature].tolist()
                        )
                    )
                })
            else :
                res['exemplar_features'].append({
                    'name': 'No genes in bin',
                    'entropy': [],
                    'counts': []
                })


    @property
    def output(self) :
        '''
        Tabular output is a table where each row corresponds to a percentile
        with the following columns:

        pct
            percentile of entropy distribution
        pctVal
            the entropy value for each percentile
        num_features
            the number of features with entropy in the corresponding
            percentile
        frac_features
            the fraction of features with entropy in the corresponding
            percentile
        cum_frac_features
            the cumulative fraction of features with entropy in the
            corresponding percentile, i.e. the fraction of features
            with pctVal entropy or higher
        exemplar_feature
            the name of a feature with an entropy in the given percentile

        '''
        res = [['pct','pctVal','num_features','frac_features','cum_frac_features','exemplar_feature']]

        fields = [self['entropies'][_] for _ in res[0][:-1]]
        exemplar_names = [[_['name'] for _ in self['entropies']['exemplar_features']]]
        res.extend(list(zip(*fields+exemplar_names)))

        return res
    @property
    def properties(self) :
        '''
        The key entropies contains a single object with following keys:

        pct
            percentile of entropy distribution
        pctVal
            the entropy value for each percentile
        num_features
            the number of features with entropy in the corresponding
            percentile
        frac_features
            the fraction of features with entropy in the corresponding
            percentile
        cum_frac_features
            the cumulative fraction of features with entropy in the
            corresponding percentile, i.e. the fraction of features
            with pctVal entropy or higher
        exemplar_features
            an array of objects with an exemplar feature for each percentile
            with the following fields:

            name
                the name of the feature
            entropy
                the sample entropy of the feature
            counts
                array of [column name, count] pairs sorted by count
                ascending

        Example JSON output::

            {
                'pct': [0, 1, 2, 3, ...],
                'pctVal': [0, 0.1, 0.5, 0.9, ...],
                'num_features': [10, 12, 23, 100, ...],
                'frac_features': [0.001, 0.0012, 0.0023, 0.01, ...],
                'cum_frac_features': [0.001, 0.0022, 0.0045, 0.0145, ...],
                'exemplar_features': [
                    {
                        'name': 'ENSG0000055095.1',
                        'entropy': 0,
                        'counts': [ ['sampleA', 0], ['sampleB',0], ..., ['sampleN',1]]
                    },
                    {
                        'name': 'ENSG0000398715.1',
                        'entropy': 0.11,
                        'counts': [ ['sampleA', 0], ['sampleB',0], ..., ['sampleM',5]]
                    }
                ]
            }
        '''
        return {'entropies': self['entropies']}

class CountPCA(DetkModule) :
    '''
    Principal common analysis of the counts matrix.

    This module performs PCA on a provided counts matrix and returns the
    principal component weights, scores, and variances. In addition, the
    weights and scores for each individual component can be combined to define
    the projection of each sample along that component.  

    The PCA module can also use a counts matrix that has associated column data
    information about the samples in each column. The user can specify some of
    these columns to include as variables for plotting purposes. The idea is
    that columns labeled with the same class will be colored according to their
    class, such that separations in the data can be more easily observed when
    projections are plotted.
    '''
    def __init__(self,count_mat) :

        # get counts from file and scale counts
        # counts matrices are n_features x n_samples, need to transpose
        # since PCA expects n_samples x n_features
        cnts = scale(count_mat.counts.values.astype(float).T)

        # perform PCA and fit to the data
        pca = PCA(n_components=min(*cnts.shape))
        pca.fit(cnts)
        X = pca.transform(cnts)

        # get sample names
        sample_names = list(count_mat.counts.columns)

        # format output
        self['column_names'] = sample_names
        self['column_variables'] = {}

        # if metadata option is given, get column variables
        if count_mat.column_data is not None :
            columns = []
            for k,v in count_mat.column_data.iteritems() :
                if k != 'counts' :
                    columns.append({'column':k,'values':v.tolist()})
            self['column_variables'] = {
                'sample_names': count_mat.column_data.index.tolist(),
                'columns': columns
            }

        self['components'] = []
        for i in range(0, pca.n_components_):
            comp = {}
            comp['name'] = 'PC' + str(i+1)
            comp['scores'] = [row[i] for row in X]
            comp['projections'] = [row[i] for row in pca.components_]
            comp['perc_variance'] =  pca.explained_variance_ratio_[i]
            if np.isnan(comp['perc_variance']) :
                raise Exception('nan encountered in calculating PCA component '
                        'percent variance, this means the counts features have '
                        'zero total variance, cannot compute PCA. Examine your '
                        'counts matrix if you did not expect this?')
            self['components'].append(comp)
    @property
    def name(self):
        return 'pca'
    @property
    def output(self) :
        '''
        Tabular output is a table where each row corresponds to a column
        in the counts matrix with the following fields:

        name
            name of the column for the row
        PC*X*_*YY*
            projections of principal component X (e.g. 1) that explains YY
            percent of the variance for each column 
        '''
        res = [['colname']+self['column_names']]
        for comp in self['components'] :
            name = '{}_{:03d}'.format(comp['name'],int(100*comp['perc_variance']))
            res.append([name]+comp['projections'])
        # transpose the list of lists
        res = list(zip(*res))
        return res
    @property
    def properties(self) :
        '''
        Example JSON output::

            [
                'name': 'pca',
                'stats': {
                    'column_names': ['sample1','sample2',...],
                    'column_variables': {
                        'sample_names': ['sample1','sample2',...],
                        'columns': [
                            {
                                'column':'status',
                                'values':['disease','control',...]
                            },
                            {
                                'column':'batch',
                                'values':['b1','b1',...]
                            },
                    },
                    'components': [
                        {
                            'name': 'PC1',
                            'scores': [0.126,0.975,...], # length n
                            'projections': [-8.01,5.93,...], # length m, ordered by 'column_names'
                            'perc_variance': 0.75
                        },
                        {
                            'name': 'PC2',
                            'scores' : [0.126,0.975,...], # length n
                            'projections': [5.93,-5.11,...], # length m
                            'perc_variance': 0.22
                        }
                    ]
                }
            ]
        '''
        return {
                'column_names': self['column_names'],
                'column_variables': self['column_variables'],
                'components': self['components']
               }

def main(argv=sys.argv) :

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

    args = docopt(cmd_opts_aug[cmd],argv)
    counts_obj = make_cli_count_obj(args)
    set_logging(args)
    logger.info('cmd: %s',' '.join(argv))

    if cmd == 'pca' :
        if args['--column-data'] is not None :
            if args['<cov_fn>'] is not None :
                logger.warn('Both positional <cov_fn> argument and --column-data '
                    'are provided, ignoring the --column-data argument.'
                    )
            else :
                logger.warn('The --column-data command line argument is deprecated. '
                        'Use the optional [<cov_fn>] positional argument instead.'
                    )

                args['<cov_fn>'] = args['--column-data']

        counts_obj = make_cli_count_obj(args)
        output = CountPCA(counts_obj)

    elif cmd == 'summary' :
        if args['--column-data'] is not None :
            if args['<cov_fn>'] is not None :
                logger.warn('Both positional <cov_fn> argument and --column-data '
                    'are provided, ignoring the --column-data argument.'
                    )
            else :
                logger.warn('The --column-data command line argument is deprecated. '
                        'Use the optional [<cov_fn>] positional argument instead.'
                    )

                args['<cov_fn>'] = args['--column-data']

        counts_obj = make_cli_count_obj(args)
        output = summary(counts_obj
          ,int(args['--bins'])
          ,args['--log']
          ,args['--density']
        )
    elif cmd == 'coldist' :
        output = ColDist(counts_obj
          ,bins=int(args['--bins'])
          ,log=args['--log']
          ,density=args['--density']
        )
    elif cmd == 'rowdist' :
        output = RowDist(counts_obj
          ,bins=int(args['--bins'])
          ,log=args['--log']
          ,density=args['--density']
        )
    elif cmd == 'colzero' :
        output = ColZero(counts_obj)
    elif cmd == 'rowzero' :
        output = RowZero(counts_obj)
    elif cmd == 'entropy' :
        output = Entropy(counts_obj)
    elif cmd == 'basestats' :
        output = BaseStats(counts_obj)

    # make output a list if it is a singleton
    if not isinstance(output,list) :
        output = [output]

    #Obtain string used to name output files, unless filename is specified
    filename_prefix = os.path.splitext(args['<counts_fn>'])[0]

    outf = sys.stdout
    if args['--output'] != 'stdout' :
        outf = open(args['--output'],'wt')

    if args['--format'] == 'table' :
        from terminaltables import AsciiTable
        for out in output :
            table = AsciiTable(out.output)
            table.title = out.name
            outf.write(table.table+'\n')

    else : # csv is default
        out_writer = csv.writer(outf,delimiter=',')

        # write out the output data
        if len(output) == 1 :
            out_writer.writerows(output[0].output)
        else :
            for out in output :
                out_writer.writerow(['#{}'.format(out.name)])
                out_writer.writerows(out.output)

    # write out the report json
    if not args['--no-report'] :
        logging.info('writing report to %s',args['--report-dir'])
        with DetkReport(args['--report-dir']) as r :
            for out in output :
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
