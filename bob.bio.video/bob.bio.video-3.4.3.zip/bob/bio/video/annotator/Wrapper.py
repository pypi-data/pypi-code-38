import six
import collections
import bob.bio.base
import bob.bio.face
import logging
from . import Base, normalize_annotations

logger = logging.getLogger(__name__)


class Wrapper(Base):
  """Annotates video files using the provided image annotator.
  See the documentation of :any:`Base` too.

  Parameters
  ----------
  annotator : :any:`bob.bio.base.annotator.Annotator` or str
      The image annotator to be used. The annotator could also be the name of a
      bob.bio.annotator resource which will be loaded.
  max_age : int
      see :any:`normalize_annotations`.
  normalize : bool
      If True, it will normalize annotations using :any:`normalize_annotations`
  validator : object
      See :any:`normalize_annotations` and
      :any:`bob.bio.face.annotator.min_face_size_validator` for one example.


  Please see :any:`Base` for more accepted parameters.

  .. warning::

      You should only set ``normalize`` to True only if you are annotating
      **all** frames of the video file.

  """

  def __init__(self,
               annotator,
               normalize=False,
               validator=bob.bio.face.annotator.min_face_size_validator,
               max_age=-1,
               **kwargs
               ):
    super(Wrapper, self).__init__(**kwargs)
    self.annotator = annotator
    self.normalize = normalize
    self.validator = validator
    self.max_age = max_age

    # load annotator configuration
    if isinstance(annotator, six.string_types):
      self.annotator = bob.bio.base.load_resource(annotator, "annotator")

  def annotate(self, frames, **kwargs):
    """See :any:`Base.annotate`
    """
    annotations = collections.OrderedDict()
    for i, frame in self.frame_ids_and_frames(frames):
      logger.debug("Annotating frame %s", i)
      annotations[i] = self.annotator(frame, **kwargs)
    if self.normalize:
      annotations = collections.OrderedDict(normalize_annotations(
          annotations, self.validator, self.max_age))
    return annotations
