def normalize_annotations(annotations, validator, max_age=-1):
  """Normalizes the annotations of one video sequence. It fills the
  annotations for frames from previous ones if the annotation for the current
  frame is not valid.

  Parameters
  ----------
  annotations : collections.OrderedDict
      A dict of dict where the keys to the first dict are frame indices as
      strings (starting from 0). The inside dicts contain annotations for that
      frame. The dictionary needs to be an ordered dict in order for this to
      work.
  validator : callable
      Takes a dict (annotations) and returns True if the annotations are valid.
      This can be a check based on minimal face size for example: see
      :any:`bob.bio.face.annotator.min_face_size_validator`.
  max_age : :obj:`int`, optional
      An integer indicating for a how many frames a detected face is valid if
      no detection occurs after such frame. A value of -1 == forever

  Yields
  ------
  str
      The index of frame.
  dict
      The corrected annotations of the frame.
  """
  # the annotations for the current frame
  current = None
  age = 0

  for k, annot in annotations.items():
    if validator(annot):
      current = annot
      age = 0
    elif max_age < 0 or age < max_age:
      age += 1
    else:  # no detections and age is larger than maximum allowed
      current = None

    yield k, current


# these imports should be here to avoid circular dependencies
from .Base import Base
from .Wrapper import Wrapper
from .FailSafeVideo import FailSafeVideo


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, and not in the import module.
  Fixing sphinx warnings of not being able to find classes, when path is
  shortened.

  Parameters
  ----------
  *args
      An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args:
    obj.__module__ = __name__


__appropriate__(
    Base,
    Wrapper,
    FailSafeVideo,
)

__all__ = [_ for _ in dir() if not _.startswith('_')]
