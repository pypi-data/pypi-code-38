#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.bio.base
import bob.io.base
import os
import six

from .. import utils

class Wrapper (bob.bio.base.extractor.Extractor):
  """Wrapper class to run feature extraction algorithms on frame containers.

  Features are extracted for all frames in the frame container using the provided ``extractor``.
  The ``extractor`` can either be provided as a registered resource, i.e., one of :ref:`bob.bio.face.extractors`, or an instance of an extractor class.

  The ``frame_selector`` can be chosen to select some frames from the frame container.
  By default, all frames from the previous preprocessing step are kept, but fewer frames might be selected in this stage.

  **Parameters:**

  extractor : str or :py:class:`bob.bio.base.extractor.Extractor` instance
    The extractor to be used to extract features from the frames.

  frame_selector : :py:class:`bob.bio.video.FrameSelector`
    A frame selector class to define, which frames of the preprocessed frame container to use.

  compressed_io : bool
    Use compression to write the resulting features to HDF5 files.
    This is experimental and might cause trouble.
    Use this flag with care.
  """

  def __init__(self,
      extractor,
      frame_selector = utils.FrameSelector(selection_style='all'),
      compressed_io = False
  ):
    # load extractor configuration
    if isinstance(extractor, six.string_types):
      self.extractor = bob.bio.base.load_resource(extractor, "extractor")
    elif isinstance(extractor, bob.bio.base.extractor.Extractor):
      self.extractor = extractor
    else:
      raise ValueError("The given extractor could not be interpreted")

    self.frame_selector = frame_selector
    self.compressed_io = compressed_io
    # register extractor's details
    bob.bio.base.extractor.Extractor.__init__(
        self,
        requires_training=self.extractor.requires_training,
        split_training_data_by_client=self.extractor.split_training_data_by_client,
        extractor=extractor,
        frame_selector=frame_selector,
        compressed_io=compressed_io
    )

  def _check_feature(self, frames):
    """Checks if the given feature is in the desired format."""
    assert isinstance(frames, utils.FrameContainer)


  def __call__(self, frames):
    """__call__(frames) -> features

    Extracts the frames from the video and returns a frame container.

    This function is used to extract features using the desired ``extractor`` for all frames that are selected by the ``frame_selector`` specified in the constructor of this class.

    **Parameters:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The frame container containing preprocessed image frames.

    **Returns:**

    features : :py:class:`bob.bio.video.FrameContainer`
      A frame container containing extracted features.
    """
    self._check_feature(frames)
    # go through the frames and extract the features
    fc = utils.FrameContainer()
    for index, frame, quality in self.frame_selector(frames):
      # extract features
      extracted = self.extractor(frame)
      if extracted is not None:
        # add features to new frame container
        fc.add(index, extracted, quality)

    if not len(fc):
      return None

    return fc


  def read_feature(self, filename):
    """read_feature(filename) -> frames

    Reads the extracted data from file and returns them in a frame container.
    The extractors ``read_feature`` function is used to read the data for each frame.

    **Parameters:**

    filename : str
      The name of the extracted data file.

    **Returns:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The read frames, stored in a frame container.
    """
    if self.compressed_io:
      return utils.load_compressed(filename, self.extractor.read_feature)
    else:
      return utils.FrameContainer(bob.io.base.HDF5File(filename), self.extractor.read_feature)


  def write_feature(self, frames, filename):
    """Writes the extracted features to file.

    The extractors ``write_features`` function is used to write the features for each frame.

    **Parameters:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The extracted features for the selected frames, as returned by the `__call__` function.

    filename : str
      The file name to write the  extracted feature into.
    """
    self._check_feature(frames)
    if self.compressed_io:
      return utils.save_compressed(frames, filename, self.extractor.write_feature)
    else:
      frames.save(bob.io.base.HDF5File(filename, 'w'), self.extractor.write_feature)


  def train(self, training_frames, extractor_file):
    """Trains the feature extractor with the preprocessed data of the given frames.

    .. note::
       This function is not called, when the given ``extractor`` does not require training.

    This function will train the feature extractor using all data from the selected frames of the training data.
    The training_frames must be aligned by client if the given ``extractor`` requires that.

    **Parameters:**

    training_frames : [:py:class:`bob.bio.video.FrameContainer`] or [[:py:class:`bob.bio.video.FrameContainer`]]
      The set of training frames, which will be used to train the ``extractor``.

    extractor_file : str
      The name of the extractor that should be written.
    """
    if self.split_training_data_by_client:
      [self._check_feature(frames) for client_frames in training_frames for frames in client_frames]
      features = [[frame[1] for frames in client_frames for frame in self.frame_selector(frames)] for client_frames in training_frames]
    else:
      [self._check_feature(frames) for frames in training_frames]
      features = [frame[1] for frames in training_frames for frame in self.frame_selector(frames)]
    self.extractor.train(features, extractor_file)


  def load(self, extractor_file):
    """Loads the trained extractor from file.

    This function calls the wrapped classes ``load`` function.

    extractor_file : str
      The name of the extractor that should be loaded.
    """
    self.extractor.load(extractor_file)
