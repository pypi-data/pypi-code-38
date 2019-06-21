from . import Base
import bob.bio.face
import collections
import logging
import six

logger = logging.getLogger(__name__)


class FailSafeVideo(Base):
  """A fail-safe video annotator.
  It tries several annotators in order and tries the next one if the previous
  one fails. However, the difference between this annotator and
  :any:`bob.bio.base.annotator.FailSafe` is that this one tries to use
  annotations from older frames (if valid) before trying the next annotator.

  .. warning::

      You must be careful in using this annotator since different annotators
      could have different results. For example the bounding box of one
      annotator be totally different from another annotator.

  Parameters
  ----------
  annotators : :any:`list`
      A list of annotators to try.
  max_age : int
      The maximum number of frames that an annotation is valid for next frames.
      This value should be positive. If you want to set max_age to infinite,
      then you can use the :any:`bob.bio.video.annotator.Wrapper` instead.
  validator : callable
      A function that takes the annotations of a frame and validates it.


  Please see :any:`Base` for more accepted parameters.
  """

  def __init__(self, annotators, max_age=15,
               validator=bob.bio.face.annotator.min_face_size_validator,
               **kwargs):
    super(FailSafeVideo, self).__init__(**kwargs)
    assert max_age > 0, "max_age: `{}' cannot be less than 1".format(max_age)
    self.annotators = []
    for annotator in annotators:
      if isinstance(annotator, six.string_types):
        annotator = bob.bio.base.load_resource(annotator, 'annotator')
      self.annotators.append(annotator)
    self.max_age = max_age
    self.validator = validator

  def annotate(self, frames, **kwargs):
    """See :any:`Base.annotate`
    """
    annotations = collections.OrderedDict()
    current = None
    age = 0
    for i, frame in self.frame_ids_and_frames(frames):
      for annotator in self.annotators:
        annot = annotator.annotate(frame, **kwargs)
        if annot and self.validator(annot):
          current = annot
          age = 0
          break
        elif age < self.max_age:
          age += 1
          break
        else:  # no detections and age is larger than maximum allowed
          current = None

        if current is not annot:
          logger.debug("Annotator `%s' failed.", annotator)

      annotations[i] = current
    return annotations
