#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import six
import bob.bio.base
import bob.io.base

from .. import utils

class Wrapper (bob.bio.base.algorithm.Algorithm):
  """Wrapper class to run face recognition algorithms on video data.

  This class provides a generic interface for all face recognition algorithms to use several frames of a video.
  The ``algorithm`` can either be provided as a registered resource, or an instance of an extractor class.
  Already in previous stages, features were extracted from only some selected frames of the image.
  This algorithm now uses these features to perform face recognition, i.e., by enrolling a model from several frames (possibly of several videos), and fusing scores from several model frames and several probe frames.
  Since the functionality to handle several images for enrollment and probing is already implemented in the wrapped class, here we only care about providing the right data at the right time.

  **Parameters:**

  algorithm :  str or :py:class:`bob.bio.base.algorithm.Algorithm` instance
    The algorithm to be used.

  frame_selector : :py:class:`bob.bio.video.FrameSelector`
    A frame selector class to define, which frames of the extracted features of the frame container to use.
    By default, all features are selected.

  compressed_io : bool
    Use compression to write the projected features to HDF5 files.
    This is experimental and might cause trouble.
    Use this flag with care.

  """
  def __init__(self,
      algorithm,
      frame_selector = utils.FrameSelector(selection_style='all'),
      compressed_io = False
  ):
    # load algorithm configuration
    if isinstance(algorithm, six.string_types):
      self.algorithm = bob.bio.base.load_resource(algorithm, "algorithm")
    elif isinstance(algorithm, bob.bio.base.algorithm.Algorithm):
      self.algorithm = algorithm
    else:
      raise ValueError("The given algorithm could not be interpreted")

    bob.bio.base.algorithm.Algorithm.__init__(
        self,
        self.algorithm.performs_projection,
        self.algorithm.requires_projector_training,
        self.algorithm.split_training_features_by_client,
        self.algorithm.use_projected_features_for_enrollment,
        self.algorithm.requires_enroller_training,
        algorithm=algorithm,
        frame_selector=frame_selector,
        compressed_io=compressed_io
    )

    self.frame_selector = frame_selector
    # if we select the frames during feature extraction, for enrollment we use all files
    # otherwise select frames during enrollment (or enroller training)
    self.enroll_frame_selector = (lambda i : i) if self.use_projected_features_for_enrollment else frame_selector
    self.compressed_io = compressed_io


  def _check_feature(self, frames):
    """Checks if the given feature is in the desired format."""
    assert isinstance(frames, utils.FrameContainer)

  # PROJECTION

  def train_projector(self, training_frames, projector_file):
    """Trains the projector with the features of the given frames.

    .. note::
       This function is not called, when the given ``algorithm`` does not require projector training.

    This function will train the projector using all data from the selected frames of the training data.
    The training_frames must be aligned by client if the given ``algorithm`` requires that.

    **Parameters:**

    training_frames : [:py:class:`bob.bio.video.FrameContainer`] or [[:py:class:`bob.bio.video.FrameContainer`]]
      The set of training frames, which will be used to perform projector training of the ``algorithm``.

    extractor_file : str
      The name of the projector that should be written.
    """
    if self.split_training_features_by_client:
      [self._check_feature(frames) for client_frames in training_frames for frames in client_frames]
      training_features = [[frame[1] for frames in client_frames for frame in self.frame_selector(frames)] for client_frames in training_frames]
    else:
      [self._check_feature(frames) for frames in training_frames]
      training_features = [frame[1] for frames in training_frames for frame in self.frame_selector(frames)]
    self.algorithm.train_projector(training_features, projector_file)


  def load_projector(self, projector_file):
    """Loads the trained extractor from file.

    This function calls the wrapped classes ``load_projector`` function.

    projector_file : str
      The name of the projector that should be loaded.
    """
    return self.algorithm.load_projector(projector_file)


  def project(self, frames):
    """project(frames) -> projected

    Projects the frames from the extracted frames and returns a frame container.

    This function is used to project features using the desired ``algorithm`` for all frames that are selected by the ``frame_selector`` specified in the constructor of this class.

    **Parameters:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The frame container containing extracted feature frames.

    **Returns:**

    projected : :py:class:`bob.bio.video.FrameContainer`
      A frame container containing projected features.
    """
    self._check_feature(frames)
    fc = utils.FrameContainer()
    for index, frame, quality in self.frame_selector(frames):
      # extract features
      projected = self.algorithm.project(frame)
      # add image to frame container
      fc.add(index, projected, quality)
    return fc


  def read_feature(self, projected_file):
    """read_feature(projected_file) -> frames

    Reads the projected data from file and returns them in a frame container.
    The algorithms ``read_feature`` function is used to read the data for each frame.

    **Parameters:**

    filename : str
      The name of the projected data file.

    **Returns:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The read frames, stored in a frame container.
    """
    if self.compressed_io:
      return utils.load_compressed(projected_file, self.algorithm.read_feature)
    else:
      return utils.FrameContainer(bob.io.base.HDF5File(projected_file), self.algorithm.read_feature)


  def write_feature(self, frames, projected_file):
    """Writes the projected features to file.

    The extractors ``write_features`` function is used to write the features for each frame.

    **Parameters:**

    frames : :py:class:`bob.bio.video.FrameContainer`
      The projected features for the selected frames, as returned by the :py:meth:`project` function.

    projected_file : str
      The file name to write the  projetced feature into.
    """
    self._check_feature(frames)
    if self.compressed_io:
      return utils.save_compressed(frames, projected_file, self.algorithm.write_feature)
    else:
      frames.save(bob.io.base.HDF5File(projected_file, 'w'), self.algorithm.write_feature)


  # ENROLLMENT

  def train_enroller(self, training_frames, enroller_file):
    """Trains the enroller with the features of the given frames.

    .. note::
       This function is not called, when the given ``algorithm`` does not require enroller training.

    This function will train the enroller using all data from the selected frames of the training data.

    **Parameters:**

    training_frames : [[:py:class:`bob.bio.video.FrameContainer`]]
      The set of training frames aligned by client, which will be used to perform enroller training of the ``algorithm``.

    enroller_file : str
      The name of the enroller that should be written.
    """
    [self._check_feature(frames) for client_frames in training_frames for frames in client_frames]
    features = [[frame[1] for frames in client_frames for frame in self.enroll_frame_selector(frames)] for client_frames in training_frames]
    self.algorithm.train_enroller(features, enroller_file)

  def load_enroller(self, enroller_file):
    """Loads the trained enroller from file.

    This function calls the wrapped classes ``load_enroller`` function.

    enroller_file : str
      The name of the enroller that should be loaded.
    """
    self.algorithm.load_enroller(enroller_file)


  def enroll(self, enroll_frames):
    """enroll(enroll_frames) -> model

    Enrolls the model from features of all selected frames of all enrollment videos for the current client.

    This function collects all desired frames from all enrollment videos and enrolls a model with that, using the algorithms ``enroll`` function.

    **Parameters:**

    enroll_frames : [:py:class:`bob.bio.video.FrameContainer`]
      Extracted or projected features from one or several videos of the same client.

    **Returns:**

    model : object
      The model as created by the algorithms ``enroll`` function.
    """
    [self._check_feature(frames) for frames in enroll_frames]
    features = [frame[1] for frames in enroll_frames for frame in self.enroll_frame_selector(frames)]
    return self.algorithm.enroll(features)


  def write_model(self, model, filename):
    """Writes the model using the algorithm's ``write_model`` function.

    **Parameters:**

    model : object
      The model returned by the :py:meth:`enroll` function.

    filename : str
      The file name of the model to write.
    """
    self.algorithm.write_model(model, filename)


  # SCORING

  def read_model(self, filename):
    """Reads the model using the algorithms ``read_model`` function.

    **Parameters:**

    filename : str
      The file name to read the model from.

    **Returns:**

    model : object
      The model read from file.
    """
    return self.algorithm.read_model(filename)

  def score(self, model, probe):
    """score(model, probe) -> score

    Computes the score between the given model and the probe.

    As the probe is a frame container, several scores are computed, one for each frame of the probe.
    This is achieved by using the algorithms ``score_for_multiple_probes`` function.
    The final result is, hence, a fusion of several scores.

    **Parameters:**

    model : object
      The model in the type desired by the wrapped algorithm.

    probe : :py:class:`bob.bio.video.FrameContainer`
      The selected frames from the probe objects, which contains the probes are desired by the wrapped algorithm.

    **Returns:**

    score : float
      A fused score between the given model and all probe frames.
    """
    features = [frame[1] for frame in self.frame_selector(probe)]
    return self.algorithm.score_for_multiple_probes(model, features)


  def score_for_multiple_probes(self, model, probes):
    """score_for_multiple_probes(model, probes) -> score

    Computes the score between the given model and the given list of probes.

    As each probe is a frame container, several scores are computed, one for each frame of each probe.
    This is achieved by using the algorithms ``score_for_multiple_probes`` function.
    The final result is, hence, a fusion of several scores.

    **Parameters:**

    model : object
      The model in the type desired by the wrapped algorithm.

    probes : [:py:class:`bob.bio.video.FrameContainer`]
      The selected frames from the probe objects, which contains the probes are desired by the wrapped algorithm.

    **Returns:**

    score : float
      A fused score between the given model and all probe frames.
    """
    [self._check_feature(frames) for frames in probes]
    probe = [frame[1] for frame in probe for probe in probes]
    return self.algorithm.score_for_multiple_probes(model, probe)

  # re-define some functions to avoid them being falsely documented
  def score_for_multiple_models(*args,**kwargs): raise NotImplementedError("This function is not implemented and should not be called.")
