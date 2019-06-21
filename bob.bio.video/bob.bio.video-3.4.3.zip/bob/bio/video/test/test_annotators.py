import os
import collections
import bob.io.base
import bob.io.image
import bob.io.video
import bob.bio.video
import pkg_resources
from bob.bio.video.test.dummy.database import DummyBioFile
from bob.bio.face.test.test_annotators import _assert_bob_ip_facedetect


class FailSucessAnnotator(bob.bio.base.annotator.Annotator):
  """An annotator that fails for every second time it is called."""

  def __init__(self, **kwargs):
    super(FailSucessAnnotator, self).__init__(**kwargs)
    self.failed_last_time = True

  def annotate(self, image, **kwargs):
    if not self.failed_last_time:
      self.failed_last_time = True
      return None
    else:
      self.failed_last_time = False
      return {
          'topleft': (0, 0),
          'bottomright': (64, 64)
      }


def test_wrapper():

  original_path = pkg_resources.resource_filename("bob.bio.face.test", "")
  image_files = DummyBioFile(client_id=1, file_id=1, path="data/testimage")

  # video preprocessor using a face crop preprocessor
  annotator = bob.bio.video.annotator.Wrapper('facedetect')

  # read original data
  original = annotator.read_original_data(
      image_files, original_path, ".jpg")

  assert isinstance(original, bob.bio.video.FrameContainer)
  assert len(original) == 1
  assert original[0][0] == os.path.basename(
      image_files.make_path(original_path, ".jpg"))

  # annotate data
  annot = annotator(original)

  assert isinstance(annot, collections.OrderedDict), annot
  _assert_bob_ip_facedetect(annot['testimage.jpg'])


def test_wrapper_normalize():

  original_path = pkg_resources.resource_filename("bob.bio.video.test", "")
  video_object = bob.bio.video.database.VideoBioFile(
      client_id=1, file_id=1, path="data/testvideo")
  # here I am using 3 frames to test normalize but in real applications this
  # should not be done.
  frame_selector = bob.bio.video.FrameSelector(
      max_number_of_frames=3, selection_style="spread")

  annotator = bob.bio.video.annotator.Wrapper(
      'flandmark', frame_selector=frame_selector, normalize=True)
  video = annotator.read_original_data(video_object, original_path, ".avi")
  assert isinstance(video, bob.bio.video.FrameContainer)

  annot = annotator(video)

  # check if annotations are ordered by frame number
  assert list(annot.keys()) == sorted(annot.keys(), key=int), annot


def test_failsafe_video():

  original_path = pkg_resources.resource_filename("bob.bio.video.test", "")
  video_object = bob.bio.video.database.VideoBioFile(
      client_id=1, file_id=1, path="data/testvideo")
  # here I am using 3 frames to test normalize but in real applications this
  # should not be done.
  frame_selector = bob.bio.video.FrameSelector(
      max_number_of_frames=3, selection_style="spread")

  annotator = bob.bio.video.annotator.FailSafeVideo(
      [FailSucessAnnotator(), 'facedetect'], frame_selector=frame_selector)
  video = annotator.read_original_data(video_object, original_path, ".avi")
  assert isinstance(video, bob.bio.video.FrameContainer)

  annot = annotator(video)

  # check if annotations are ordered by frame number
  assert list(annot.keys()) == sorted(annot.keys(), key=int), annot

  # check if the failsuccess annotator was used for all frames
  for _, annotations in annot.items():
    assert 'topleft' in annotations, annot
    assert annotations['topleft'] == (0, 0), annot
    assert annotations['bottomright'] == (64, 64), annot
