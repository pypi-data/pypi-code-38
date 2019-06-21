#!/usr/bin/env python

from bob.pad.face.extractor import FrameDiffFeatures

#=======================================================================================
# Define instances here:

window_size = 20
overlap = 0

frame_diff_feat_extr_w20_over0 = FrameDiffFeatures(
    window_size=window_size, overlap=overlap)
