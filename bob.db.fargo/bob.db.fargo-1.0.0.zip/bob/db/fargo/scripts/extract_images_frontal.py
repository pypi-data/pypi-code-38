#!/usr/bin/env python
# encoding: utf-8

"""

    Frontal face image extractor for the FARGO videos (%(version)s)

    This script will extract 10 frontal face images from the 
    original recorded sequences, in each of the modalities.
   

Usage:
  %(prog)s <dbdir> 
           [--imagesdir=<path>] [--interval=<int>] 
           [--verbose ...] [--plot]

Options:
  -h, --help                Show this screen.
  -V, --version             Show version.
  -i, --imagesdir=<path>    Where to store saved images [default: ./images]
      --interval=<int>      Interval [*10ms] between saved images [default: 4]
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
import subprocess
import bob.io.video
import bob.io.base
import bob.io.image

from bob.db.fargo.utils import load_timestamps

def find_closest_frame_index(color_time, other_timestamps):
  """ finds the closest (depth or NIR) frame to the current (color) frame.

  Parameters
  ----------
  color_time : int
    Timestamp [ms] of the current color frame
  other_timestamps: dict
    Dictionary with the frame index and the 
    corresponding timestamp for the other stream

  Returns
  -------
  int:
    Index of the closest frame
  
  """
  return_index = -1
  diff = sys.maxsize
  for index in other_timestamps:
    if abs(other_timestamps[index] - color_time) < diff:
      diff = abs(other_timestamps[index] - color_time)
      return_index = index
  return return_index


def load_timestamps(filename):
  """ load timestamps of a recording.
  
  Each line of the file contains two numbers: 
  the frame index and the corresponding time in milliseconds.
  
  Parameters
  ----------
  filename: str
    The file to extract timestamps from.

  Returns
  -------
  dict:
    Dictionary with frame index as key and timestamp as value.
  """
  timestamps = {}
  f = open(filename, 'r')
  for line in f:
    line = line.rstrip('\n')
    splitted = line.split(' ')
    timestamps[int(splitted[0])] = int(splitted[1])   
  f.close()
  return timestamps


def get_first_annotated_frame_index(filename):
  """ determines the frame index of the first annotated frame.
 
  It is based on the timestamps file provided with the annotations of
  particular recording.

  This timestamps file provides both the frame index and corresponding timestamp
  for all images that have been manually annotated in the recording.

  Note that if the file does not exists, this function considers that
  the frame index of the first annotated frame is 0 at time 0
  
  Parameters
  ----------
  filename: str
    The file with annotations timestamps. 

  Returns
  -------
  list of tuples:
    List of (frame_index, timestamp) for annotated frames in the sequence.
  int:
    Status of the process (-1 meaning failure)

  """
  status = 0 
  try:
    f = open(filename, 'r')
    first_line = f.readline().rstrip()
    first_line = first_line.split(' ')
    indices = (int(first_line[0]), int(first_line[1]))
    f.close()
  except IOError:
    status = -1 
    indices = (0, 0)
  return indices, status


def check_if_recording_is_ok(recording_dir):
  """ checks if the processing of an existing recording is complete.

  This function goes recursively through the folder where the images
  (in each modality) from this recording are supposed to have been saved. 
  Returns True if every file supposed to be there is present, and False otherwise.

  This helps resuming when the script was stopped. 

  Parameters
  ----------
  recording_dir : str 
    The path where extracted images from this recording are supposed to be saved.

  Returns
  -------
  bool:
    True if everything is there, False otherwise
  
  """
  color_dir = os.path.join(recording_dir, 'color')
  ir_dir = os.path.join(recording_dir, 'ir')
  depth_dir = os.path.join(recording_dir, 'depth')

  for index in range(10):
    filename = os.path.join(color_dir, '{:0>2d}.png'.format(index))
    if not os.path.isfile(filename):
      return False
    filename = os.path.join(ir_dir, '{:0>2d}.png'.format(index))
    if not os.path.isfile(filename):
      return False
    filename = os.path.join(depth_dir, '{:0>2d}.png'.format(index))
    if not os.path.isfile(filename):
      return False
  
  return True

def preprocess_depth(depth_data):
  """ preprocess depth data 

  This function "reverses" the original recorded data, and
  convert data into grayscale pixel value.

  The higher the value of a pixel, the closer to the camera.

  Parameters
  ----------
  depth_data : numpy.ndarray
    The data coming from the depth channel 

  Returns
  -------
  numpy.ndarray :
    The preprocessed depth data, to be saved as an image
  
  """
  # get background / foreground (i.e. zero-valued pixels are considered as background)
  background = numpy.where(depth_data <= 0)
  foreground = numpy.where(depth_data > 0)
  
  # trick such that the highest value is the closest to the sensor
  depth_data = depth_data * (-1)
  max_significant = numpy.max(depth_data[foreground])
  min_significant = numpy.min(depth_data[foreground])

  # normalize to 0-255 and set background to zero
  new_depth_data = 255 * ((depth_data - min_significant) / float(max_significant -  min_significant))
  new_depth_data[background] = 0
  return new_depth_data
 

def main(user_input=None):
  """ Main function to extract frontal images from recorded streams.
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
  if not os.path.isdir(args['--imagesdir']):
    os.makedirs(args['--imagesdir'])

  # counters
  no_data_counter = 0
  missing_timestamps_counter = 0
  misalignement_counter = 0
  no_annotations_counter = 0
  no_annotated_frame_counter = 0
  
  for subject in os.listdir(base_dir):
    for session in ['controlled', 'dark', 'outdoor']: 
      for condition in ['SR300-laptop', 'SR300-mobile']:
        for recording in ['0', '1']:
          
          logger.info("===== Subject {0}, session {1}, device {2}, recording {3} ...".format(subject, session, condition, recording))
          recording_dir = os.path.join(base_dir, subject, session, condition, recording)

          # create directories to save the extracted data
          save_base_dir = os.path.join(args['--imagesdir'], subject, session, condition, recording)
          if not os.path.isdir(save_base_dir):
            os.makedirs(save_base_dir)
          if not os.path.isdir(os.path.join(save_base_dir, 'color')):
            os.makedirs(os.path.join(save_base_dir, 'color'))
          if not os.path.isdir(os.path.join(save_base_dir, 'ir')):
            os.makedirs(os.path.join(save_base_dir, 'ir'))
          if not os.path.isdir(os.path.join(save_base_dir, 'depth')):
            os.makedirs(os.path.join(save_base_dir, 'depth'))

          # check if the recording has already been processed, and if so, that everything is ok  
          if check_if_recording_is_ok(save_base_dir):
            logger.info("recording already processed and ok")
            continue
          
          # original data directories
          color_dir = os.path.join(recording_dir, 'streams', 'color')
          ir_dir = os.path.join(recording_dir, 'streams', 'ir')
          depth_dir = os.path.join(recording_dir, 'streams', 'depth')

          # uncompress the 7z archive - both ir and depth - if needed
          if (len(os.listdir(ir_dir))) == 1 and ('ir.7z' in os.listdir(ir_dir)):
            logger.debug("uncompressing NIR")
            ir_compressed = os.path.join(ir_dir, 'ir.7z')
            command = "7z x -y -o" + ir_dir + ' ' + ir_compressed
            try:
              p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
              stdoutdata, stderrdata = p.communicate()
            except:
              pass
          if (len(os.listdir(depth_dir))) == 1 and ('depth.7z' in os.listdir(depth_dir)):
            logger.debug("uncompressing depth")
            depth_compressed = os.path.join(depth_dir, 'depth.7z')
            command = "7z x -y -o" + depth_dir + ' ' + depth_compressed
            try:
              p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
              stdoutdata, stderrdata = p.communicate()
            except:
              pass

          # process color file
          color_file = os.path.join(color_dir, 'color.264')
          if os.path.isfile(color_file):
            color_stream = bob.io.video.reader(color_file)
          else:
            logger.warn('[NO DATA] {0}\n'.format(recording_dir))
            no_data_counter += 1
            continue

          # get the timestamps of the color frames
          try:
            color_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'color_timestamps.txt'))
            ir_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'ir_timestamps.txt'))
            depth_timestamps = load_timestamps(os.path.join(base_dir, subject, session, condition, recording, 'streams', 'depth_timestamps.txt'))
          except IOError:
            logger.warn('[MISSING TIMESTAMPS] {0}'.format(recording_dir))
            missing_timestamps_counter += 1

          # get the index of the first annotated frame in the stream
          first_annotated_frame_indices, status = get_first_annotated_frame_index(os.path.join(recording_dir, 'annotations', 'color_timestamps.txt'))
          if status < 0:
            logger.warn('[NO ANNOTATIONS] {0}'.format(recording_dir))
            no_annotations_counter += 1 
          logger.debug("First annotated frame is frame #{0}, at time {1}".format(first_annotated_frame_indices[0], first_annotated_frame_indices[1]))
          
          # loop on the color stream
          interval = int(args['--interval'])
          saved_image_index = 0
          last_frame_index = first_annotated_frame_indices[0] + (10 * interval)
          
          for i, frame in enumerate(color_stream):
            
            # get the frames of interest (the frame every "interval")
            toto = i - first_annotated_frame_indices[0]
            if toto % interval == 0 and i < last_frame_index:

              # save color image
              saved_png = os.path.join(save_base_dir, 'color', '{:0>2d}.png'.format(saved_image_index))
              bob.io.base.save(frame, saved_png)
              
              # find the closest ir frame, and save the image 
              ir_index = find_closest_frame_index(color_timestamps[toto], ir_timestamps)
              logger.debug("Image {}: Closest IR frame is at {} with index {} (color is at {})".format(saved_image_index, ir_timestamps[ir_index], ir_index, color_timestamps[toto]))
              ir_file = os.path.join(ir_dir, '{0}.bin'.format(ir_index))
              with open(ir_file) as irf:
                ir_data = numpy.fromfile(irf, dtype=numpy.int16).reshape(-1, 640)
                # kind of normalization that looks OK
                ir_image = ir_data / 4.0 
                saved_ir_image = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'ir', '{:0>2d}.png'.format(saved_image_index))
                bob.io.base.save(ir_image.astype('uint8'), saved_ir_image)
              
              # find the closest depth frame, and save the image 
              depth_index = find_closest_frame_index(color_timestamps[toto], depth_timestamps)
              logger.debug("Image {}: Closest depth frame is at {} with index {} (color is at {})".format(saved_image_index, depth_timestamps[depth_index], depth_index, color_timestamps[toto]))
              depth_file = os.path.join(depth_dir, '{0}.bin'.format(depth_index))
              with open(depth_file) as df:
                depth_data = numpy.fromfile(df, dtype=numpy.int16).reshape(-1, 640)
                depth_image = preprocess_depth(depth_data)
                saved_depth = os.path.join(args['--imagesdir'], subject, session, condition, recording, 'depth', '{:0>2d}.png'.format(saved_image_index))
                bob.io.base.save(depth_image.astype('uint8'), saved_depth)
  
              # plot saved data if asked for
              if bool(args['--plot']):
                from matplotlib import pyplot
                f, axarr = pyplot.subplots(1, 3)
                pyplot.suptitle('frame {0} at time {1} saved'.format(toto, color_timestamps[toto]))
                axarr[0].imshow(numpy.rollaxis(numpy.rollaxis(frame, 2),2))
                axarr[0].set_title("Color")
                axarr[1].imshow(ir_image, cmap='gray')
                axarr[1].set_title("NIR")
                axarr[2].imshow(depth_data, cmap='gray')
                axarr[2].set_title("Depth")
                pyplot.show()
              
              saved_image_index += 1
           
            # stop when done saving the number of desired images
            if i > last_frame_index:
              break

  logger.info('[NO DATA] -> {}'.format(no_data_counter))
  logger.info('[MISSING TIMESTAMPS] -> {}'.format(missing_timestamps_counter))
  logger.info('[NO ANNOTATIONS] -> {}'.format(no_annotations_counter))
  logger.info('[NO ANNOTATED FRAME] -> {}'.format(no_annotated_frame_counter))
  logger.info('[MISALIGNMENT] -> {}'.format(misalignement_counter))
