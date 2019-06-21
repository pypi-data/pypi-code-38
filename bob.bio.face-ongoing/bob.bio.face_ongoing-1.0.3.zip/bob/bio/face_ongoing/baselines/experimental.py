#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
from bob.bio.base.baseline import Baseline


# idiap_casia_inception_v2_centerloss_gray
preprocessors = dict()        
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["ijbc"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")
preprocessors["ijba"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")

experimental = Baseline(name = "experimental",\
                                                    extractor = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/casiawebface/experimental.py"),\
                                                    algorithm = 'distance-cosine',\
                                                    preprocessors=preprocessors
)

