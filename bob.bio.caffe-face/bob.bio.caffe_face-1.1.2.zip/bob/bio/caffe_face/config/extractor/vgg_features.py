#!/usr/bin/env python

import bob.bio.caffe_face
extractor = bob.bio.caffe_face.extractor.VGGFeatures(
    feature_layer="fc7"
)
