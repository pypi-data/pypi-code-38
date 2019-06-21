#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import numpy
import bob.io.base
import bob.io.base.test_utils
import bob.io.image
import bob.io.video

import bob.bio.base
import bob.bio.video

regenerate_refs = False

def test_frame_container():
  # Test that bob.bio.base.load and save works as expected
  filename = bob.io.base.test_utils.temporary_filename()

  try:
    # create random test data
    test_data = [numpy.random.randn(20,20) for i in range(15)]
    frames = bob.bio.video.FrameContainer()
    for i in range(15):
      frames.add(i, test_data[i], i/5.)

    # write to file
    frames.save(bob.io.base.HDF5File(filename, 'w'))
    # read from file using the dummy class
    read = bob.bio.video.FrameContainer(bob.io.base.HDF5File(filename, 'r'))

    assert len(read) == 15

    # assert that the data hasn't changed and also order is kept
    for i, (index, data, quality) in enumerate(read):
      index = int(index)
      assert index == i
      assert abs(quality - index/5.) < 1e-8
      assert numpy.allclose(test_data[i], data)

    # test as_array method
    assert numpy.allclose(read.as_array(), test_data)

  finally:
    if os.path.exists(filename):
      os.remove(filename)


def test_frame_selector():
  # tests frame selector capabilities
  file_names = ['path%d/image%d.jpg' % (i,i) for i in range(10)]

  def image_load_function(s):
    assert s in file_names
    return os.path.dirname(s)

  # first frames, limited to the actual number of frames
  frame_selector = bob.bio.video.FrameSelector(selection_style = 'first', max_number_of_frames = 20)
  frames = frame_selector(file_names, image_load_function)
  assert len(frames) == 10
  assert [f[1] for f in frames] == [image_load_function(s) for s in file_names]

  # all frames
  frame_selector = bob.bio.video.FrameSelector(selection_style = 'all')
  frames = frame_selector(file_names, image_load_function)
  assert len(frames) == 10
  assert [f[0] for f in frames] == [os.path.basename(s) for s in file_names]
  assert [f[1] for f in frames] == [image_load_function(s) for s in file_names]

  # step-wise frames
  frame_selector = bob.bio.video.FrameSelector(selection_style = 'step', step_size = 4, max_number_of_frames = 2)
  frames = frame_selector(file_names, image_load_function)
  assert len(frames) == 2
  assert frames[0][0] == os.path.basename(file_names[2])
  assert frames[0][1] == image_load_function(file_names[2])
  assert frames[0][2] is None
  assert frames[1][0] == os.path.basename(file_names[6])
  assert frames[1][1] == image_load_function(file_names[6])
  assert frames[1][2] is None

  # spread frames
  frame_selector = bob.bio.video.FrameSelector(selection_style = 'spread', max_number_of_frames = 3)
  frames = frame_selector(file_names, image_load_function)
  assert len(frames) == 3
  indices = bob.bio.base.selected_indices(10, 3)
  for i in range(3):
    assert frames[i][0] == os.path.basename(file_names[indices[i]])
    assert frames[i][1] == image_load_function(file_names[indices[i]])
    assert frames[i][2] is None

  # simple string data; load video
  video_name = "video_name.avi"
  video_data = numpy.random.randn(10,20,20)
  def video_load_function(v):
    assert v == video_name
    return video_data.copy()

  frame_selector = bob.bio.video.FrameSelector(selection_style = 'first', max_number_of_frames = 3)
  frames = frame_selector(video_name, video_load_function)
  assert len(frames) == 3
  for i in range(3):
    assert frames[i][0] == str(i)
    assert numpy.allclose(frames[i][1], video_data[i])
    assert frames[i][2] is None

  # video data
  frame_selector = bob.bio.video.FrameSelector(selection_style = 'step', step_size = 4, max_number_of_frames = 2)
  frames = frame_selector(video_data)
  assert len(frames) == 2
  assert frames[0][0] == '2'
  assert numpy.allclose(frames[0][1], video_data[2])
  assert frames[0][2] is None
  assert frames[1][0] == '6'
  assert numpy.allclose(frames[1][1], video_data[6])
  assert frames[1][2] is None
