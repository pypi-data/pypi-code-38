#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Mon 07 Nov 2016 15:20:26 CET


"""Visualizes a particular sample throughout many processing stages

Usage: %(prog)s [-v...] [-s <path>] <database> <processed> <stem> [<stem>...]
       %(prog)s --help
       %(prog)s --version


Arguments:

  <database>   Name of the database to use for creating the model (options are:
               "fv3d" or "verafinger")
  <processed>  Path with the directory holding the preprocessed and extracted
               sub-directories containing the processing results of a
               bob.bio.vein toolchain
  <stem>       Name of the object on the database to display, without the root
               or the extension


Options:

  -h, --help                Shows this help message and exits
  -V, --version             Prints the version and exits
  -v, --verbose             Increases the output verbosity level
  -s <path>, --save=<path>  If set, saves image into a file instead of
                            displaying it


Examples:

  Visualize the processing toolchain over a single image of VERA finger vein:

     $ %(prog)s verafinger /mc client/sample

  Visualize multiple masks (like in a proof-sheet):

     $ %(prog)s verafinger /mc client/sample1 client/sample2

"""


import os
import sys

import numpy

import schema
import docopt

import bob.core
logger = bob.core.log.setup("bob.bio.vein")

import matplotlib.pyplot as mpl
from ..preprocessor import utils

import bob.io.base
import bob.io.image


def save_figures(title, image, mask, image_pp, binary):
  '''Saves individual images on a directory


  Parameters:

    title (str): A title for this plot

    image (numpy.ndarray): The original image representing the finger vein (2D
      array with dtype = ``uint8``)

    mask (numpy.ndarray): A 2D boolean array with the same size of the original
      image containing the pixels in which the image is valid (``True``) or
      invalid (``False``).

    image_pp (numpy.ndarray): A version of the original image, pre-processed by
      one of the available algorithms

    binary (numpy.ndarray): A binarized version of the original image in which
      all pixels (should) represent vein (``True``) or not-vein (``False``)

  '''

  os.makedirs(title)
  bob.io.base.save(image, os.path.join(title, 'original.png'))

  # add preprocessed image
  from ..preprocessor import utils
  img = utils.draw_mask_over_image(image_pp, mask)
  img = numpy.array(img).transpose(2,0,1)
  bob.io.base.save(img[:3], os.path.join(title, 'preprocessed.png'))

  # add binary image
  bob.io.base.save(binary.astype('uint8')*255, os.path.join(title,
    'binarized.png'))


def proof_figure(title, image, mask, image_pp, binary=None):
  '''Builds a proof canvas out of individual images


  Parameters:

    title (str): A title for this plot

    image (numpy.ndarray): The original image representing the finger vein (2D
      array with dtype = ``uint8``)

    mask (numpy.ndarray): A 2D boolean array with the same size of the original
      image containing the pixels in which the image is valid (``True``) or
      invalid (``False``).

    image_pp (numpy.ndarray): A version of the original image, pre-processed by
      one of the available algorithms

    binary (numpy.ndarray, Optional): A binarized version of the original image
      in which all pixels (should) represent vein (``True``) or not-vein
      (``False``)


  Returns:

    matplotlib.pyplot.Figure: A figure canvas containing the proof for the
    particular sample on the database

  '''

  fig = mpl.figure(figsize=(6,9), dpi=100)

  images = 3 if binary is not None else 2

  # add original image
  mpl.subplot(images, 1, 1)
  mpl.title('%s - original' % title)
  mpl.imshow(image, cmap="gray")

  # add preprocessed image
  from ..preprocessor import utils
  img = utils.draw_mask_over_image(image_pp, mask)
  mpl.subplot(images, 1, 2)
  mpl.title('Preprocessed')
  mpl.imshow(img)

  if binary is not None:
    # add binary image
    mpl.subplot(3, 1, 3)
    mpl.title('Binarized')
    mpl.imshow(binary.astype('uint8')*255, cmap="gray")

  return fig


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
    '<database>': schema.And(lambda n: n in valid_databases,
      error='<database> must be one of %s' % ', '.join(valid_databases)),
    str: object, #ignores strings we don't care about
    }, ignore_extra_keys=True)

  return sch.validate(args)


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

  # Loads the image, the mask and save it to a PNG file
  for stem in args['<stem>']:
    f = [k for k in all_files if k.path == stem]
    if len(f) == 0:
      raise RuntimeError('File with stem "%s" does not exist on "%s"' % \
          (stem, args['<database>']))
    f = f[0]
    image = f.load(db.original_directory, db.original_extension)
    pp_name = f.make_path(os.path.join(args['<processed>'], 'preprocessed'),
        extension='.hdf5')
    pp = bob.io.base.HDF5File(pp_name)
    mask  = pp.read('mask')
    image_pp = pp.read('image')
    try:
      binary = f.load(os.path.join(args['<processed>'], 'extracted'))
      binary = numpy.rot90(binary, k=1)
    except:
      binary = None
    fig = proof_figure(stem, image, mask, image_pp, binary)
    if args['--save']:
      save_figures(args['--save'], image, mask, image_pp, binary)
    else:
      mpl.show()
      print('Close window to continue...')
