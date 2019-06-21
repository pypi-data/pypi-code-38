#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import bob.bio.base
import bob.bio.base.test.dummy.extractor
import bob.bio.video
import bob.io.base
import bob.io.base.test_utils
import bob.io.image
import bob.io.video

import pkg_resources

regenerate_refs = False


def test_extractor():
  filename = bob.io.base.test_utils.temporary_filename()

  try:
    # load test data
    preprocessed_video_file = pkg_resources.resource_filename("bob.bio.video.test", "data/preprocessed.hdf5")

    preprocessor = bob.bio.video.preprocessor.Wrapper('face-crop-eyes', compressed_io=False)
    preprocessed_video = preprocessor.read_data(preprocessed_video_file)

    extractor = bob.bio.video.extractor.Wrapper(bob.bio.base.test.dummy.extractor.DummyExtractor(), compressed_io=False)
    extractor.train([preprocessed_video]*5, filename)

    assert os.path.exists(filename)

    extractor2 = bob.bio.video.extractor.Wrapper("dummy", compressed_io=False)
    extractor2.load(filename)

    extracted = extractor2(preprocessed_video)
    assert isinstance(extracted, bob.bio.video.FrameContainer)

    reference_file = pkg_resources.resource_filename("bob.bio.video.test", "data/extracted.hdf5")
    if regenerate_refs:
      extracted.save(bob.io.base.HDF5File(reference_file, 'w'))
    reference_data = bob.bio.video.FrameContainer(bob.io.base.HDF5File(reference_file, 'r'))

    assert extracted.is_similar_to(reference_data)
  finally:
    if os.path.exists(filename):
      os.remove(filename)
