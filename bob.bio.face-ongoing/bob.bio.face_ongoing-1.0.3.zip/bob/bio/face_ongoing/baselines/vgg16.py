#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
from bob.bio.base.baseline import Baseline

# idiap_casia_inception_v2_centerloss_gray
preprocessors = dict()        
preprocessors["default"] = 'face-head-vgg'
preprocessors["mobio"] = 'face-eyes-vgg'
preprocessors["fargo"] = 'face-eyes-vgg'

vgg16 = Baseline(name = "vgg16",\
                 extractor = 'vgg_features',\
                 algorithm = 'distance-cosine',\
                 preprocessors=preprocessors)
