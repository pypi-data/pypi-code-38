#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Mon 24 Apr 09:35:40 CEST 2017

""" Create videos sequence from 3DMAD HDF5 data (%(version)s) 

Usage:
  %(prog)s  <datadir> <outdir>
           [--force] [--gridcount] 
           [--verbose ...] [--show]

Options:

  Options:
  -h, --help                  Show this screen.
  -V, --version               Show version.
  -f, --force                 Overwrite existing cropped image files.
  -G, --gridcount             Display the number of objects and exits.
  -v, --verbose               Increase the verbosity (may appear multiple times).
  -s, --show                  Show original face and annotations, and the cropped face. 

Example:

  To run the conversion process 
    
    $ %(prog)s path/to/orignal/data path/to/video_sequences

See '%(prog)s --help' for more information.

"""

import os
import sys
import pkg_resources

from docopt import docopt

version = pkg_resources.require('bob.db.maskattack')[0].version

import numpy
import math

import bob.io.base
import bob.io.video
import bob.db.maskattack
import bob.ip.draw

import bob.core
logger = bob.core.log.setup("bob.db.maskattack")

import gridtk

def filter_for_sge_task(l):
  '''Breaks down a list of objects as per SGE task requirements'''

  # identify which task I am running on
  task_id = int(os.environ['SGE_TASK_ID'])
  logger.debug('SGE_TASK_ID=%d' % task_id)
  task_first = int(os.environ['SGE_TASK_FIRST'])
  logger.debug('SGE_TASK_FIRST=%d' % task_first)
  task_last = int(os.environ['SGE_TASK_LAST'])
  logger.debug('SGE_TASK_LAST=%d' % task_last)
  task_step = int(os.environ['SGE_TASK_STEPSIZE'])
  logger.debug('SGE_TASK_STEPSIZE=%d' % task_step)

  # build a list of tasks, like the SGE manager has
  tasks = list(range(task_first, task_last+1, task_step))

  # creates an array with the limits of each task
  length = len(l)
  limits = list(range(0, length, int(math.ceil(float(length)/len(tasks)))))

  # get the index of the slot for the given task id
  task_index = tasks.index(task_id)

  # yields only the elements for the current slot
  if task_id != tasks[-1]: # not the last
    logger.info('[SGE task %d/%d] Returning entries %d:%d out of %d samples',
        task_index+1, len(tasks), limits[task_index], limits[task_index+1],
        len(l))
    return l[limits[task_index]:limits[task_index+1]]
  else: # it is the last
    logger.info('[SGE: task %d/%d] Returning entries %d:%d out of %d samples',
        task_index+1, len(tasks), limits[task_index], len(l), len(l))
    return l[limits[task_index]:]


def main(user_input=None):
  """
  
  Main function to convert 3DMAD HDF5 data to video sequences

  """

  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Face cropping (%s)' % version,)

  # set verbosity level 
  bob.core.log.set_verbosity_level(logger, args['--verbose'])

  db = bob.db.maskattack.Database(original_directory='/idiap/resource/database/3dmad/Data',
                                  original_extension='.hdf5')
  objs = db.objects()

  # if we are on a grid environment, just find what I have to process.
  #if os.environ.has_key('SGE_TASK_ID'):
  try:
    os.environ['SGE_TASK_ID']
    objs = filter_for_sge_task(objs) 
  except:
    pass

  if args['--gridcount']:
    print (len(objs))
    sys.exit()

  seq_dir = os.path.join(args['<outdir>'], 'sequences')
  pos_dir = os.path.join(args['<outdir>'], 'annotations')
  if not os.path.isdir(seq_dir):
    os.makedirs(seq_dir)
  if not os.path.isdir(pos_dir):
    os.makedirs(pos_dir)

  # counters
  seq_counter = 1

  # === LET'S GO ===
  for obj in objs:

    logger.info("Processing sequence {} ({}/{})".format(obj.make_path(directory=args['<datadir>']), seq_counter, len(objs)))
    filename = obj.make_path(directory=args['<datadir>'])

    f = bob.io.base.HDF5File(filename)
    Color = f.read('Color_Data')
    pos = f.read('Eye_Pos')
    
    # create the annotation file
    pos_filename = os.path.join(pos_dir, obj.path + '.face')
    pos_file = open(pos_filename, 'w')
    frame_counter = 0
    for i in range(pos.shape[0]):
      pos_file.write("{} {} {} {} {}\n".format(frame_counter, int(pos[i,1]), int(pos[i,0]), int(pos[i,3]), int(pos[i,2])))
      frame_counter += 1
    pos_file.close()
    
    out_filename = os.path.join(seq_dir, obj.path + '.avi')
    if os.path.isfile(out_filename) and not args['--force']:
      logger.warn("{} already exists -> skipping !".format(out_filename))
      continue
    color_video = bob.io.video.writer(out_filename, Color.shape[-2], Color.shape[-1], 30)
    if Color.shape[1]<3:
        color_video.append(numpy.concatenate((Color,Color,Color),1))
    else:
        color_video.append(Color)
    color_video.close()
    del f
    seq_counter += 1
