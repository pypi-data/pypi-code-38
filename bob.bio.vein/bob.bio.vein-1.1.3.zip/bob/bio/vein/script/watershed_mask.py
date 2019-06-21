#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Wed  4 Oct 11:23:52 2017 CEST


"""Preprocesses a fingervein image with a watershed/neural-net seeded mask

Usage: %(prog)s [-v...] [-s <path>] [-f <float>] [-b <float>] [--scan]
                <model> <database> [<stem>...]
       %(prog)s --help
       %(prog)s --version


Arguments:

  <model>     Path to model to use for find watershed markers
  <database>  Name of the database to use for creating the model (options are:
              "fv3d" or "verafinger")
  <stem>      Name of the object on the database to display, without the root
              or the extension. If none provided, run for all possible stems on
              the database


Options:

  -h, --help                  Shows this help message and exits
  -V, --version               Prints the version and exits
  -v, --verbose               Increases the output verbosity level
  -f, --fg-threshold=<float>  Foreground threshold value. Should be set to a
                              number that is between 0.5 and 1.0. The higher,
                              the less markers for the foreground watershed
                              process will be produced. [default: 0.7]
  -b, --bg-threshold=<float>  Background threshold value. Should be set to a
                              number that is between 0.0 and 0.5. The smaller,
                              the less markers for the foreground watershed
                              process will be produced. [default: 0.3]
  -S, --scan                  If set, ignores settings for the threshold and
                              scans the whole range of threshold printing the
                              Jaccard, M1 and M2 merith figures
  -s <path>, --save=<path>    If set, saves individual image into files instead
                              of displaying the result of processing. Pass the
                              name of directory that will be created and
                              suffixed with the paths of original images.


Examples:

  Visualize the preprocessing toolchain over a single image

     $ %(prog)s model.hdf5 verafinger sample-stem

  Save the results of the preprocessing to several files. In this case, the
  program runs non-interactively:

     $ %(prog)s -s graphics model.hdf5 verafinger sample-stem

  Scans the set of possible thresholds printing Jaccard, M1 and M2 indexes:

     $ %(prog)s --scan model.hdf5 verafinger sample-stem

"""


import os
import sys
import time

import numpy

import schema
import docopt

import bob.core
logger = bob.core.log.setup("bob.bio.vein")

import matplotlib.pyplot as plt

import bob.io.base
import bob.io.image


def validate(args):
  '''Validates command-line arguments, returns parsed values

  This function uses :py:mod:`schema` for validating :py:mod:`docopt`
  arguments. Logging level is not checked by this procedure (actually, it is
  ignored) and must be previously setup as some of the elements here may use
  logging for outputing information.


  Parameters:

    args (dict): Dictionary of arguments as defined by the help message and
      returned by :py:mod:`docopt`


  Returns

    dict: Validate dictionary with the same keys as the input and with values
      possibly transformed by the validation procedure


  Raises:

    schema.SchemaError: in case one of the checked options does not validate.

  '''

  valid_databases = ('fv3d', 'verafinger')

  sch = schema.Schema({
    '<model>': schema.And(os.path.exists,
      error='<model> should point to an existing path'),
    '<database>': schema.And(lambda n: n in valid_databases,
      error='<database> must be one of %s' % ', '.join(valid_databases)),
    '--fg-threshold': schema.And(
      schema.Use(float), lambda n: 0.5 < n < 1.0,
      error='--fg-threshold should be a float between 0.5 and 1.0',
      ),
    '--bg-threshold': schema.And(
      schema.Use(float), lambda n: 0.0 < n < 0.5,
      error='--bg-threshold should be a float between 0.0 and 0.5',
      ),
    str: object, #ignores strings we don't care about
    }, ignore_extra_keys=True)

  return sch.validate(args)


def save_figures(title, image, markers, edges, mask):
  '''Saves individual images on a directory
  '''

  dirname = os.path.dirname(title)
  if not os.path.exists(dirname): os.makedirs(dirname)
  bob.io.base.save(image, os.path.join(title, 'original.png'))

  _ = markers.copy().astype('uint8')
  _[_==1] = 128
  bob.io.base.save(_, os.path.join(title, 'markers.png'))

  bob.io.base.save((255*edges).astype('uint8'), os.path.join(title,'edges.png'))

  bob.io.base.save(mask.astype('uint8')*255, os.path.join(title, 'mask.png'))

  from ..preprocessor.utils import draw_mask_over_image

  masked_image = draw_mask_over_image(image, mask)
  masked_image.save(os.path.join(title, 'masked.png'))


def make_figure(image, markers, edges, mask):
  '''Returns a matplotlib figure with the detailed processing result'''

  plt.clf() #completely clears the current figure
  figure = plt.gcf()
  plt.subplot(2,2,1)
  _ = markers.copy().astype('uint8')
  _[_==1] = 128
  plt.imshow(_, cmap='gray')
  plt.title('Markers')

  plt.subplot(2,2,2)
  _ = numpy.dstack([
      (_ | (255*edges).astype('uint8')),
      _,
      _,
      ])
  plt.imshow(_)
  plt.title('Edges')

  plt.subplot(2,2,3)
  plt.imshow(mask.astype('uint8')*255, cmap='gray')
  plt.title('Mask')

  plt.subplot(2,2,4)
  plt.imshow(image, cmap='gray')
  red_mask = numpy.dstack([
      (~mask).astype('uint8')*255,
      numpy.zeros_like(image),
      numpy.zeros_like(image),
      ])
  plt.imshow(red_mask, alpha=0.15)
  plt.title('Image (masked)')

  return figure


def process_one(args, image, path):
  '''Processes a single image'''

  from bob.bio.vein.preprocessor import WatershedMask, AnnotatedRoIMask

  # loads the processor once - avoids re-reading weights from the disk
  processor = WatershedMask(
      model=args['<model>'],
      foreground_threshold=args['--fg-threshold'],
      background_threshold=args['--bg-threshold'],
      )

  annotator = AnnotatedRoIMask()

  from bob.bio.vein.preprocessor.utils import \
      jaccard_index, intersect_ratio, intersect_ratio_of_complement

  start = time.time()
  markers, edges, mask = processor.run(image)
  total_time = time.time() - start

  # error
  annotated_mask = annotator(image)
  ji = jaccard_index(annotated_mask, mask)
  m1 = intersect_ratio(annotated_mask, mask)
  m2 = intersect_ratio_of_complement(annotated_mask, mask)
  logger.debug('%s, %.2f, %.2f, %.2f, %g, %g, %g', path, total_time,
    args['--fg-threshold'], args['--bg-threshold'], ji, m1, m2)

  if not args['--scan']:

    if args['--save']:
      dest = os.path.join(args['--save'], path)
      save_figures(dest, image, markers, edges, mask)
    else:
      fig = make_figure(image, markers, edges, mask)
      fig.suptitle('%s @ %s - JI=%.4f, M1=%.4f, M2=%.4f\n' \
          '($\\tau_{FG}$ = %.2f - $\\tau_{BG}$ = %.2f)' % \
          (path, args['<database>'], ji, m1, m2, args['--fg-threshold'],
            args['--bg-threshold']), fontsize=12)
      print('Close the figure to continue...')
      plt.show()

  return (path, total_time, args['--fg-threshold'], args['--bg-threshold'],
      ji, m1, m2)


def eval_best_thresholds(results):
  '''Evaluates the best thresholds taking into consideration various indexes'''

  m1 = numpy.array([k[-2] for k in results])
  m2 = numpy.array([k[-1] for k in results])
  index = m1/m2
  return index.argmax()


def main(user_input=None):

  if user_input is not None:
    argv = user_input
  else:
    argv = sys.argv[1:]

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

  try:
    from .validate import setup_logger
    logger = setup_logger('bob.bio.vein', args['--verbose'])
    args = validate(args)
  except schema.SchemaError as e:
    sys.exit(e)

  if args['<database>'] == 'fv3d':
    from ..configurations.fv3d import database as db
  elif args['<database>'] == 'verafinger':
    from ..configurations.verafinger import database as db

  database_replacement = "%s/.bob_bio_databases.txt" % os.environ["HOME"]
  db.replace_directories(database_replacement)
  all_files = db.objects()

  # if a specific <stem> was not provided, run for all possible stems
  if not args['<stem>']:
    args['<stem>'] = [k.path for k in all_files]

  # Loads the image, the mask and save it to a PNG file
  for stem in args['<stem>']:
    f = [k for k in all_files if k.path == stem]
    if len(f) == 0:
      raise RuntimeError('File with stem "%s" does not exist on "%s"' % \
          stem, args['<database>'])

    f = f[0]
    image = f.load(db.original_directory, db.original_extension)

    if args['--scan']:
      results = []
      logger.debug('stem, time, fg_thres, bg_thres, jaccard, m1, m2')
      for fg_threshold in numpy.arange(0.6, 1.0, step=0.1):
        for bg_threshold in numpy.arange(0.1, 0.5, step=0.1):
          args['--fg-threshold'] = fg_threshold
          args['--bg-threshold'] = bg_threshold
          results.append(process_one(args, image, f.path))
      best_thresholds = eval_best_thresholds(results)
      logger.info('%s: FG = %.2f | BG = %.2f | M1/M2 = %.2f', f.path,
        results[best_thresholds][2], results[best_thresholds][3],
        results[best_thresholds][-2]/results[best_thresholds][-1])
    else:
      process_one(args, image, f.path)
