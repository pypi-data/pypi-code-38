#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.bio.base
import bob.io.base
import bob.io.image
import bob.io.video
import numpy
import os
import six

import logging
logger = logging.getLogger("bob.bio.video")

from .FrameContainer import FrameContainer

class FrameSelector:
  """A class for selecting frames from videos.
  In total, up to ``max_number_of_frames`` is selected (unless selection style is ``all``

  Different selection styles are supported:

  * first : The first frames are selected
  * spread : Frames are selected to be taken from the whole video
  * step : Frames are selected every ``step_size`` indices, starting at ``step_size/2`` **Think twice if you want to have that when giving FrameContainer data!**
  * all : All frames are stored unconditionally
  * quality (only valid for FrameContainer data) : Select the frames based on the highest internally stored quality value
  """

  def __init__(self,
      max_number_of_frames = 20,
      selection_style = "spread",
      step_size = 10
  ):
    if selection_style not in ('first', 'spread', 'step', 'all'):
      raise ValueError("Unknown selection style '%s', choose one of ('first', 'spread', 'step', 'all')" % selection_style)
    self.selection = selection_style
    self.max_frames = max_number_of_frames
    self.step = step_size

  def __call__(self, data, load_function = bob.io.base.load):
    """Selects frames and returns them in a FrameContainer.
    Different ``data`` parameters are accepted:

    * :py:class:`FrameContainer` : frames are selected from the given frame container
    * ``str`` : A video file to read and select frames from
    * ``[str]`` : A list of image names to select from
    * ``numpy.array`` (3D or 4D): A video to select frames from

    When giving ``str`` or ``[str]`` data, the given ``load_function`` is used to read the data from file.
    """
    # if given a string, first load the video
    if isinstance(data, six.string_types):
      logger.debug("Loading video file '%s'", data)
      data = load_function(data)

    # first, get the indices
    count = len(data)
    if self.selection == 'first':
      # get the first frames (limited by all frames)
      indices = range(0, min(count, self.max_frames))
    elif self.selection == 'spread':
      # get frames lineraly spread over all frames
      indices = bob.bio.base.selected_indices(count, self.max_frames)
    elif self.selection == 'step':
      indices = range(self.step//2, count, self.step)[:self.max_frames]
    elif self.selection == 'all':
      indices = range(0, count)

    # now, iterate through the data
    fc = FrameContainer()
    if isinstance(data, FrameContainer):
      indices = set(indices)
      # frame container data, just copy
      for i, frame in enumerate(data):
        if i in indices:
          fc.add(*frame)
    elif isinstance(data, numpy.ndarray):
      # select video frames
      for i in indices:
        fc.add(i, data[i])
    elif isinstance(data, list):
      for i in indices:
        # load image
        image = load_function(data[i])
        # save image name as well
        fc.add(os.path.basename(data[i]), image)

    return fc

  def __str__(self):
    """Writes the parameters of the FrameSelector as a string."""
    return "FrameSelector(max_number_of_frames=%d, selection_style='%s', step_size=%d)" % (self.max_frames, self.selection, self.step)
