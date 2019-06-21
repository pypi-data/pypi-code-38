#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Compares two set of masks and prints some error metrics

This program requires that the masks for both databases (one representing the
ground-truth and a second the database with an automated method) are
represented as HDF5 files containing a ``mask`` object, which should be boolean
in nature.


Usage: %(prog)s [-v...] [-n X] <ground-truth> <database>
       %(prog)s --help
       %(prog)s --version


Arguments:
  <ground-truth>  Path to a set of files that contain ground truth annotations
                  for the ROIs you wish to compare.
  <database>      Path to a similar set of files as in `<ground-truth>`, but
                  with ROIs calculated automatically. Every HDF5 in this
                  directory will be matched to an equivalent file in the
                  `<ground-truth>` database and their masks will be compared


Options:
  -h, --help          Shows this help message and exits
  -V, --version       Prints the version and exits
  -v, --verbose       Increases the output verbosity level
  -n N, --annotate=N  Print out the N worst cases available in the database,
                      taking into consideration the various metrics analyzed


Example:

  1. Just run for basic statistics:

     $ %(prog)s -vvv gt/ automatic/

  2. Identify worst 5 samples in the database according to a certain criterion:

     $ %(prog)s -vv -n 5 gt/ automatic/

"""

import os
import sys
import fnmatch
import operator

import numpy

import bob.core
logger = bob.core.log.setup("bob.bio.vein")

import bob.io.base


def make_catalog(d):
  """Returns a catalog dictionary containing the file stems available in ``d``

  Parameters:

    d (str): A path representing a directory that will be scanned for .hdf5
      files


  Returns

    list: A list of stems, from the directory ``d``, that represent files of
    type HDF5 in that directory. Each file should contain two objects:
    ``image`` and ``mask``.

  """

  logger.info("Scanning directory `%s'..." % d)
  retval = []
  for path, dirs, files in os.walk(d):
    basedir = os.path.relpath(path, d)
    logger.debug("Scanning sub-directory `%s'..." % basedir)
    candidates = fnmatch.filter(files, '*.hdf5')
    if not candidates: continue
    logger.debug("Found %d files" % len(candidates))
    retval += [os.path.join(basedir, k) for k in candidates]
  logger.info("Found a total of %d files at `%s'" % (len(retval), d))
  return sorted(retval)


def sort_table(table, cols):
  """Sorts a table by multiple columns


  Parameters:

    table (:py:class:`list` of :py:class:`list`): Or tuple of tuples, where
      each inner list represents a row

    cols (list, tuple): Specifies the column numbers to sort by e.g. (1,0)
      would sort by column 1, then by column 0


  Returns:

    list: of lists, with the table re-ordered as you see fit.

  """

  for col in reversed(cols):
      table = sorted(table, key=operator.itemgetter(col))
  return table


def mean_std_for_column(table, column):
  """Calculates the mean and standard deviation for the column in question


  Parameters:

    table (:py:class:`list` of :py:class:`list`): Or tuple of tuples, where
      each inner list represents a row

    col (int): The number of the column from where to extract the data for
      calculating the mean and the standard-deviation.


  Returns:

    float: mean

    float: (unbiased) standard deviation

  """

  z = numpy.array([k[column] for k in table])
  return z.mean(), z.std(ddof=1)


def main(user_input=None):

  if user_input is not None:
    argv = user_input
  else:
    argv = sys.argv[1:]

  import docopt
  import pkg_resources

  completions = dict(
      prog=os.path.basename(sys.argv[0]),
      version=pkg_resources.require('bob.bio.vein')[0].version
      )

  args = docopt.docopt(
      __doc__ % completions,
      argv=argv,
      version=completions['version'],
      )

  # Sets-up logging
  verbosity = int(args['--verbose'])
  bob.core.log.set_verbosity_level(logger, verbosity)

  # Catalogs
  gt = make_catalog(args['<ground-truth>'])
  db = make_catalog(args['<database>'])

  if gt != db:
    raise RuntimeError("Ground-truth and database have different files!")

  # Calculate all metrics required
  from ..preprocessor import utils
  metrics = []
  for k in gt:
    gt_file = os.path.join(args['<ground-truth>'], k)
    db_file = os.path.join(args['<database>'], k)
    gt_roi = bob.io.base.HDF5File(gt_file).read('mask')
    db_roi = bob.io.base.HDF5File(db_file).read('mask')
    metrics.append((
      k,
      utils.jaccard_index(gt_roi, db_roi),
      utils.intersect_ratio(gt_roi, db_roi),
      utils.intersect_ratio_of_complement(gt_roi, db_roi),
      ))
    logger.info("%s: JI = %.5g, M1 = %.5g, M2 = %5.g" % metrics[-1])

  # Print statistics
  names = (
      (1, 'Jaccard index'),
      (2, 'Intersection ratio (m1)'),
      (3, 'Intersection ratio of complement (m2)'),
      )
  print("Statistics:")
  for k, name in names:
    mean, std = mean_std_for_column(metrics, k)
    print(name + ': ' + '%.2e +- %.2e' % (mean, std))

  # Print worst cases, if the user asked so
  if args['--annotate'] is not None:
    N = int(args['--annotate'])
    if N <= 0:
      raise docopt.DocoptExit("Argument to --annotate should be >0")

    print("Worst cases by metric:")
    for k, name in names:
      print(name + ':')

      if k in (1,2):
        worst = sort_table(metrics, (k,))[:N]
      else:
        worst = reversed(sort_table(metrics, (k,))[-N:])

      for n, l in enumerate(worst):
        fname = os.path.join(args['<database>'], l[0])
        print('  %d. [%.2e] %s' % (n, l[k], fname))
