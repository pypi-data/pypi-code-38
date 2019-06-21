#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import numpy
import bob.bio.base
import bob.bio.base.test.dummy.algorithm
import bob.bio.video
import bob.io.base
import bob.io.base.test_utils
import bob.io.image
import bob.io.video

from nose.plugins.skip import SkipTest
import pkg_resources

regenerate_refs = False

def test_algorithm():
  filename = bob.io.base.test_utils.temporary_filename()

  # load test data
  extracted_file = pkg_resources.resource_filename("bob.bio.video.test", "data/extracted.hdf5")
  extractor = bob.bio.video.extractor.Wrapper('dummy', compressed_io=False)
  extracted = extractor.read_feature(extracted_file)

  # use video tool with dummy face recognition tool, which contains all required functionality
  algorithm = bob.bio.video.algorithm.Wrapper(bob.bio.base.test.dummy.algorithm.DummyAlgorithm(), compressed_io=False)

  try:
    # projector training
    algorithm.train_projector([extracted] * 25, filename)
    assert os.path.exists(filename)

    algorithm2 = bob.bio.video.algorithm.Wrapper("bob.bio.base.test.dummy.algorithm.DummyAlgorithm()", compressed_io=False)
    # load projector; will perform checks internally
    algorithm2.load_projector(filename)

    projected = algorithm2.project(extracted)
    reference_file = pkg_resources.resource_filename("bob.bio.video.test", "data/projected.hdf5")
    if regenerate_refs:
      algorithm.write_feature(projected, reference_file)

    projected2 = algorithm.read_feature(reference_file)
    assert projected.is_similar_to(projected2)

  finally:
    if os.path.exists(filename):
      os.remove(filename)

  try:
    # perform enroller training
    algorithm.train_enroller([[projected] * 5] * 5, filename)
    assert os.path.exists(filename)

    # load projector; will perform checks internally
    algorithm2.load_enroller(filename)

    # enroll features
    model = algorithm2.enroll([projected] * 5)
    reference_file = pkg_resources.resource_filename("bob.bio.video.test", "data/model.hdf5")
    if regenerate_refs:
      algorithm.write_model(model, reference_file)

    model2 = algorithm2.read_model(reference_file)
    assert numpy.allclose(model, model2)

  finally:
    if os.path.exists(filename):
      os.remove(filename)

  # score
  score = algorithm.score(model, projected)
  ref = 751.924863
  assert abs(score - ref) < 1e-4, "The score %f is not close to %f" % (score, ref)
