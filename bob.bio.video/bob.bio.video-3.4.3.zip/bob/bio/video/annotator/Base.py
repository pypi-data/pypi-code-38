import bob.bio.base
from .. import utils


class Base(bob.bio.base.annotator.Annotator):
  """The base class for video annotators.

  Parameters
  ----------
  frame_selector : :any:`bob.bio.video.FrameSelector`
    A frame selector class to define, which frames of the video to use.
  read_original_data : callable
    A function with the signature of
    ``data = read_original_data(biofile, directory, extension)``
    that will be used to load the data from biofiles. By default the
    ``frame_selector`` is used to load the data.
  """

  def __init__(self, frame_selector=utils.FrameSelector(selection_style='all'),
               read_original_data=None, **kwargs):

    def _read_video_data(biofile, directory, extension):
      """Read video data using the frame_selector of this object"""
      if hasattr(biofile, 'frames'):
        return biofile.frames
      return biofile.load(directory, extension, frame_selector)

    if read_original_data is None:
      read_original_data = _read_video_data

    super(Base, self).__init__(read_original_data=read_original_data, **kwargs)

  @staticmethod
  def frame_ids_and_frames(frames):
    """Takes the frames and yields frame_ids and frames.

    Parameters
    ----------
    frames : :any:`bob.bio.video.FrameContainer` or an iterable of arrays
        The frames of the video file.

    Yields
    ------
    frame_id : str
        A string that represents the frame id.
    frame : :any:`numpy.array`
        The frame of the video file as an array.
    """
    if isinstance(frames, utils.FrameContainer):
      for fid, fr, _ in frames:
        yield fid, fr
    else:
      for fid, fr in enumerate(frames):
        yield str(fid), fr

  def annotate(self, frames, **kwargs):
    """Annotates videos.

    Parameters
    ----------
    frames : :any:`bob.bio.video.FrameContainer` or :any:`numpy.array`
        The frames of the video file.
    **kwargs
        Extra arguments that annotators may need.

    Returns
    -------
    collections.OrderedDict
        A dictionary where its key is the frame id as a string and its value
        is a dictionary that are the annotations for that frame.


    .. note::

        You can use the :any:`Base.frame_ids_and_frames` functions to normalize
        the input in your implementation.
    """
    raise NotImplementedError()
