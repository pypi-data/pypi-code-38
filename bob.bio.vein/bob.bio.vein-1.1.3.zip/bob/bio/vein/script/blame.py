#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Wed 18 Jan 2017 09:40:25 CET


"""Evaluates best/worst performers in a run given original scores

Usage: %(prog)s [-v...] [options] <score-file> [<score-file> ...]
       %(prog)s --help
       %(prog)s --version


Arguments:
  <score-file>  Path to model-by-model score files for analysis


Options:
  -h, --help           Shows this help message and exits
  -V, --version        Prints the version and exits
  -v, --verbose        Increases the output verbosity level
  -c INT, --cases=INT  Number of worst/best cases to show [default: 5]


Examples:

  1. Simple trial:

     $ %(prog)s -vv model1.txt model2.txt

  2. Change the number of cases to show:

     $ %(prog)s -vv --cases=5 model*.txt

"""


import os
import sys
import numpy

import bob.core
logger = bob.core.log.setup("bob.bio.vein")


def main(user_input=None):

  if user_input is not None:
    argv = user_input
  else:
    argv = sys.argv[1:]

  import docopt
  import pkg_resources

  completions = dict(
      prog=os.path.basename(sys.argv[0]),
      version=pkg_resources.require('bob.bio.base')[0].version
      )

  args = docopt.docopt(
      __doc__ % completions,
      argv=argv,
      version=completions['version'],
      )

  # Sets-up logging
  verbosity = int(args['--verbose'])
  bob.core.log.set_verbosity_level(logger, verbosity)

  # validates number of cases
  cases = int(args['--cases'])

  # generates a huge
  from bob.bio.base.score.load import load_score, get_negatives_positives
  scores = []
  names = {}

  length = 0
  for k in args['<score-file>']:
    model = os.path.splitext(os.path.basename(k))[0]
    length = max(length, len(model))

  for k in args['<score-file>']:
    model = os.path.splitext(os.path.basename(k))[0]
    names[model] = k
    logger.info("Loading score file `%s' for model `%s'..." % (k, model))
    s = load_score(k)

    # append a column with the model name
    m = numpy.array(len(s)*[model], dtype='<U%d' % length)
    new_dt = numpy.dtype(s.dtype.descr + [('model', m.dtype.descr)])
    sp = numpy.zeros(s.shape, dtype=new_dt)
    sp['claimed_id'] = s['claimed_id']
    sp['real_id'] = s['real_id']
    sp['test_label'] = s['test_label']
    sp['score'] = s['score']
    sp['model'] = m

    # stack into the existing scores set
    scores.append(sp)

  scores = numpy.concatenate(scores)
  genuines = scores[scores['claimed_id'] == scores['real_id']]
  genuines.sort(order='score') #ascending
  impostors = scores[scores['claimed_id'] != scores['real_id']]
  impostors.sort(order='score') #ascending

  # print
  print('The %d worst genuine scores:' % cases)
  for k in range(cases):
    print(' %d. model %s -> %s (%f)' % (k+1, genuines[k]['model'][0],
      genuines[k]['test_label'], genuines[k]['score']))

  print('The %d best genuine scores:' % cases)
  for k in range(cases):
    pos = len(genuines)-k-1
    print(' %d. model %s -> %s (%f)' % (k+1, genuines[pos]['model'][0],
      genuines[pos]['test_label'], genuines[pos]['score']))

  print('The %d worst impostor scores:' % cases)
  for k in range(cases):
    pos = len(impostors)-k-1
    print(' %d. model %s -> %s (%f)' % (k+1, impostors[pos]['model'][0],
      impostors[pos]['test_label'], impostors[pos]['score']))

  print('The %d best impostor scores:' % cases)
  for k in range(cases):
    print(' %d. model %s -> %s (%f)' % (k+1, impostors[k]['model'][0],
      impostors[k]['test_label'], impostors[k]['score']))

  return 0
