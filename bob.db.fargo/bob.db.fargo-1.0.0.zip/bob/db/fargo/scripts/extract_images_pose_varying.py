#!/usr/bin/env python
# encoding: utf-8

"""

  Pose varying image extractor for the FARGO videos (%(version)s)

  This script will extract frames of a video sequence, where the
  face is not frontal. Frames are selected making use of the 
  provided timestamps of annotated frames.

Usage:
  %(prog)s <dbdir>
           [--imagesdir=<path>] [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where to store saved images [default: ./images].
  -v, --verbose             Increase the verbosity (may appear multiple times).
  -P, --plot                Show some stuff

Example:

  To run the image extraction process

    $ %(prog)s path/to/database

See '%(prog)s --help' for more information.

"""

import os
import sys
import pkg_resources

import bob.core
logger = bob.core.log.setup("bob.db.fargo")

from docopt import docopt

version = pkg_resources.require('bob.db.fargo')[0].version

import numpy
import bob.io.video
import bob.io.base
import bob.io.image

from bob.db.fargo.utils import load_timestamps

def check_if_recording_exists(recording_dir):
  """ checks if the folders of an existing recording already exists.

  This function checks if the the directories where pose-varying images
  are supposed to be saved already exist. It also returns the number 
  of images in each folder.

  This helps resuming when the script was stopped. 

  Parameters
  ----------
  recording_dir : str 
    The path where extracted images from this recording are supposed to be saved.

  Returns
  -------
  bool:
    True if pose-varying folders exist, False otherwise
  int:
    The number of existing yaw images
  int:
    The number of existing pitch images
  
  """
  yaw_images_counter = 0
  pitch_images_counter = 0
  for folder in ['yaw', 'pitch']:
    current_dir = os.path.join(recording_dir, folder)
    if not os.path.isdir(os.path.join(current_dir)):
      return False, 0, 0
    else:
      if folder == 'yaw':
        yaw_images_counter = len(os.listdir(current_dir))
      if folder == 'pitch':
        pitch_images_counter = len(os.listdir(current_dir))
  return True, yaw_images_counter, pitch_images_counter


def retrieve_past_timestamps(ref_timestamp, streams_stamps, prev_timestamp=0):
  """ get timestamps between two annotated frames.

  Parameters
  ----------
  ref_timestamp :
    The timestamp of the annotated image.

  streams_stamps :
    Timestamps dict of the whole sequence
  
  prev_timestamp :
    The timestamp of the previously annotated image.

  Returns
  -------
  dict:
    The timestamps of the frames in between the two annotated frames 

  """
  closest_previous_index = 0 
  previous_stamps = {}
  diff = sys.maxsize
  for index in streams_stamps:
    if (streams_stamps[index] > prev_timestamp) and (streams_stamps[index] <= ref_timestamp):
      previous_stamps[index] = streams_stamps[index]
  return previous_stamps


def main(user_input=None):
  """
  
  Main function to extract images from recorded streams.
  Images are clustered according to (estimate of) pose.
  The pose is retrieved thanks to annotated images.

    # annotated frame 0: frontal
    # annotated frame 1: ~10 degrees left
    # annotated frame 2: ~20 degrees left
    # annotated frame 3: ~30 degrees left
    # annotated frame 4: ~10 degrees right
    # annotated frame 5: ~20 degrees right
    # annotated frame 6: ~30 degrees right
    # annotated frame 7: ~10 degrees top 
    # annotated frame 8: ~20 degrees top 
    # annotated frame 9: ~30 degrees top 
    # annotated frame 10: ~10 degrees bottom 
    # annotated frame 11: ~20 degrees bottom 
    # annotated frame 12: ~30 degrees bottom

  """
  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Image extractor (%s)' % version,)

  # if the user wants more verbosity, lowers the logging level
  verbosity_level = args['--verbose']
  bob.core.log.set_verbosity_level(logger, verbosity_level)

  base_dir = args['<dbdir>']
  channel = 'color'

  # to compute the mean # of images in each pose cluster 
  n_sequences = 0
  yaw_counter = 0
  pitch_counter = 0

  for subject in os.listdir(base_dir):

    # pose-varying images are only extracted for controlled conditions
    sessions = ['controlled']
   
    # only probes are extracted, hence subjects from the training set are skipped
    if int(subject) < 26:
      logger.warning("Skipping subject {}".format(subject))
      continue
    
    for session in sessions: 
      for condition in ['SR300-laptop', 'SR300-mobile']:
        for recording in ['0', '1']:
          
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))
          recording_dir = os.path.join(base_dir, subject, session, condition, recording)

          # get directories where the data resides (streams and annotation)
          annotation_dir = os.path.join(recording_dir, 'annotations')
          stream_dir = os.path.join(recording_dir, 'streams')
          
          # create directories to save the extracted data
          to_save_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, channel)
          if not os.path.isdir(to_save_dir):
            os.makedirs(to_save_dir)

          # check if the recording has already been processed
          processed, n_yaw, n_pitch = check_if_recording_exists(to_save_dir) 
          if processed:
            logger.warning("Folders {} already exist, with {} yaw and {} pitch images. (you might want to check)".format(to_save_dir, n_yaw, n_pitch))
            continue

          # load the files with the timestamps
          annotations_timestamps = load_timestamps(os.path.join(annotation_dir, channel + '_timestamps.txt'))
          stream_timestamps = load_timestamps(os.path.join(stream_dir, channel + '_timestamps.txt'))

          # load the video sequence
          seq = bob.io.video.reader(os.path.join(stream_dir, 'color', 'color.mov'))
          sequence = seq.load()
          n_sequences += 1

          # lists for pose cluster
          yaw = []
          pitch = []

          # loop on the different annotations, defining pose intervals
          indices = range(1,13,1)
          for i in indices :
            
            # retrieve the past timestamps  - up to the previous annotated image 
            previous_stamps = retrieve_past_timestamps(annotations_timestamps[i], stream_timestamps, annotations_timestamps[i-1])
            
            # get the frames in the interval
            counter = 0
            for index in sorted(previous_stamps, reverse=True):

              # check the eligibility conditions on this frame:
              # - the frame should be in the interval, 
              # - and no more than 5 frames are extracted (prevents to get too frontal images)
              if previous_stamps[index] > annotations_timestamps[i-1] and counter < 5:
                
                # yaw 
                if i == 2 or i == 3 or i == 5 or i == 6: 
                  yaw.append(sequence[index])
                
                # pitch
                if i == 8 or i == 9 or i == 11 or i == 12: 
                  pitch.append(sequence[index])
              
              counter += 1

          # save images for this sequence
          folders = ['yaw', 'pitch']
          for folder in folders:
            to_save_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording, channel, folder) 
            if not os.path.isdir(os.path.join(to_save_dir)):
              os.makedirs(to_save_dir)
            
            current_list = []
            if folder == 'yaw': current_list = yaw
            if folder == 'pitch': current_list = pitch

            k = 0
            for image in current_list:
              saved_image = os.path.join(to_save_dir, '{:0>2d}.png'.format(k))
              bob.io.base.save(image, saved_image)
              if bool(args['--plot']):
                from matplotlib import pyplot
                pyplot.imshow(numpy.rollaxis(numpy.rollaxis(image, 2),2))
                pyplot.title('image {0} for interval {1}'.format(k, folder))
                pyplot.show()
              k += 1
            
          # update stats with this sequence
          yaw_counter += len(yaw)
          pitch_counter += len(pitch)
          logger.debug("{} and {} images in yaw and pitch have been extracted".format(len(yaw), len(pitch)))

  logger.info('mean number of yaw images per sequence = {}'.format(yaw_counter/float(n_sequences)))
  logger.info('mean number of pitch images per sequence = {}'.format(pitch_counter/float(n_sequences)))
