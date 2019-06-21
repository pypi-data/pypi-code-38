#!/usr/bin/env python

from bob.bio.caffe_face.extractor import LightCNNExtractor
from bob.bio.base.extractor import CallableExtractor, SequentialExtractor
# assuming images are between 0 and 255
extractor = SequentialExtractor([
    CallableExtractor(lambda x:x / 255.0),
    LightCNNExtractor(),
])
