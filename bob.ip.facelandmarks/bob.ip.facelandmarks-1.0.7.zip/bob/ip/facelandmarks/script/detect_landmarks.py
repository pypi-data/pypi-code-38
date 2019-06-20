#!/usr/bin/env python
# encoding: utf-8

'''Face landmark detector using menpo (%(version)s)

Usage:
  %(prog)s [--verbose...] [--limit-to=<int>] [--minimum-quality=<float>]
           <input> <output>
  %(prog)s (--help | -h)
  %(prog)s (--version | -V)


Options:
  -h, --help                     Show this help message and exit
  -v, --verbose                  Increases the verbosity (may appear multiple
                                 times)
  -V, --version                  Show version
  -n, --limit-to=<int>           Only detect landmarks on the first N highest
                                 quality face detections. If not set or set to
                                 zero, then use all outputs provided by the
                                 face detector [default: 0]
  -q, --minimum-quality=<float>  Only detect landmarks on the first N highest
                                 quality face detections. If not set or set to
                                 zero, then use all outputs provided by the
                                 face detector [default: 0.0]


Examples:

  To run the keypoint detection over an image and produce an output image
  showing the detected keypoints, do:

    $ %(prog)s image.png output.png

  To dump the extracted keypoints into a machine-readable HDF5 file, do:

    $ %(prog)s image.png keypoints.hdf5

  You can also process video sequences like this:

    $ %(prog)s video.avi output.avi


See '%(prog)s --help' for more information.

'''

import os
import sys
import pkg_resources

import logging
__logging_format__='[%(levelname)s] %(message)s'
logging.basicConfig(format=__logging_format__)
logger = logging.getLogger(__name__)

from docopt import docopt

version = pkg_resources.require('bob.ip.facelandmarks')[0].version

import bob.io.base
import bob.io.video
import bob.io.image

def main(user_input=None):

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(
          prog=prog,
          version=version,
          )
  args = docopt(
      __doc__ % completions,
      argv=arguments,
      version='Face landmark detection for images and videos (%s)' % version,
      )

  # if the user wants more verbosity, lowers the logging level
  if args['--verbose'] == 1: logging.getLogger().setLevel(logging.INFO)
  elif args['--verbose'] >= 2: logging.getLogger().setLevel(logging.DEBUG)

  from ..utils import detect_landmarks, draw_landmarks, save_landmarks

  data = bob.io.base.load(args['<input>'])
  top = int(args['--limit-to'])
  if top:
    logger.info('Limiting face-detector output to the top %d detection(s)', top)
  min_quality = float(args['--minimum-quality'])
  if min_quality > 0.0:
    logger.info('Limiting face-detector by quality at %g', min_quality)
  result = detect_landmarks(data, top, min_quality)

  outext = os.path.splitext(args['<output>'])[1]
  if outext in ['.png', '.pbm', '.pnm', '.jpg', '.jpeg', '.gif', '.tiff',
      '.tif']:
    logger.info("Drawing results on output image `%s'...", args['<output>'])
    draw_landmarks(data, result)
    bob.io.base.save(data, args['<output>'])
  elif outext in ['.h5', '.hdf5', '.hdf5']:
    save_landmarks(result, args['<output>'])
  else:
    raise RuntimeError("no support to output into `%s'" % args['<output>'])

  return 0
