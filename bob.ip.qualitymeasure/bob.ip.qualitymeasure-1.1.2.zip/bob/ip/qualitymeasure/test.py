#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


'''Unit-tests for bob.ip.qualitymeasure'''

import os
import numpy as np
import nose.tools
import pkg_resources

import bob.io.base
import bob.io.base.test_utils
import bob.io.video
import bob.ip.color

from . import galbally_iqm_features as iqm
from . import msu_iqa_features as iqa

from bob.io import image
from . import remove_highlights


REF_VIDEO_FILE = 'real_client001_android_SD_scene01.mp4'
REF_FEATURE_FILE = 'real_client001_android_SD_scene01_ref_feats.h5'


def F(n):
  return pkg_resources.resource_filename(
      __name__, os.path.join('data', n))


input_video_file = F(REF_VIDEO_FILE)
assert os.path.isfile(
    input_video_file), "File: not found: %s" % input_video_file
inputVideo = bob.io.video.reader(input_video_file)
video_data = inputVideo.load()
numframes = 3


def load_reference_features():
  ref_feat_file = F(REF_FEATURE_FILE)
  assert os.path.isfile(ref_feat_file), "File: not found: %s" % ref_feat_file
  rf = bob.io.base.HDF5File(ref_feat_file)
  assert rf.has_key('/bobiqm'), "Key: /bobiqm not found in file %s" % ref_feat_file
  assert rf.has_key('/msuiqa'), "Key: /msuiqa not found in file %s" % ref_feat_file
  galbally_ref_features = rf.read('/bobiqm')
  msu_ref_features = rf.read('/msuiqa')
  del rf
  return (galbally_ref_features, msu_ref_features)


# load reference-features into global vars.
galbally_ref_features, msu_ref_features = load_reference_features()


def test_galbally_feat_extr():
  # change this, if you add more features to galbally_iqm_features module.
  iqm_len = 18
  # feature-array to hold features for several frames
  bobfset = np.zeros([numframes, iqm_len])
  f = 0

  # process first frame separately, to get the no. of iqm features
  rgbFrame = video_data[f]
  iqmSet = iqm.compute_quality_features(rgbFrame)
  numIQM = len(iqmSet)

  # test: check that numIQM is the same as expected iqm_len (18)
  nose.tools.eq_(numIQM, iqm_len)

  # store features for first frame in feature-array
  bobfset[f] = iqmSet

  # now store iqm features for remaining test-frames of input video.
  for f in range(1, numframes):
    rgbFrame = video_data[f]
    bobfset[f] = iqm.compute_quality_features(rgbFrame)

  # test: compare feature-values in bobfset[] with those loaded from hdf5 file
  nose.tools.assert_true((bobfset == galbally_ref_features).all())
  # np.allclose(A,B)


def test_msu_feat_extr():
  # change this, if you change the no. of features in msu_iqa_features module.
  iqa_len = 121
  # feature-array to hold features for several frames
  msufset = np.zeros([numframes, iqa_len])
  f = 0

  # process first frame separately, to get the no. of iqa features
  rgbFrame = video_data[f]
  iqaSet = iqa.compute_msu_iqa_features(rgbFrame)
  numIQA = len(iqaSet)

  # test: check that numIQA matches the expected iqa_len(121)
  nose.tools.eq_(numIQA, iqa_len)

  # store features for first frame in feature-array
  msufset[f] = iqaSet

  # now store iqm features for remaining test-frames of input video.
  for f in range(1, numframes):
    rgbFrame = video_data[f]
    msuQFeats = iqa.compute_msu_iqa_features(rgbFrame)
    msufset[f] = msuQFeats

  # test: compare feature-values in bobfset[] with those loaded from hdf5 file
  nose.tools.assert_true((msufset == msu_ref_features).all())

# test if the specular highlights algorithm (remove_highlights.cpp::remove_highlights)
# performs exactly like the original code from which it was mostly copied.
def test_remove_highlights_integrity():
    # open pictures
    img1 = image.load(F('old_man.ppm'))
    img2 = image.load(F('toys.ppm'))

    # compute
    sfi1, diff1, residue1 = remove_highlights(img1.astype(np.float32), 0.5)
    sfi2, diff2, residue2 = remove_highlights(img2.astype(np.float32), 0.5)

    diff1_u8 = diff1.astype('uint8')
    diff2_u8 = diff2.astype('uint8')

    # reference files
    ref1 = image.load(F('old_man_diffuse.ppm'))
    ref2 = image.load(F('toys_diffuse.ppm'))

    # test: compare results
    assert (diff1_u8 == ref1).all()
    assert (diff2_u8 == ref2).all()
