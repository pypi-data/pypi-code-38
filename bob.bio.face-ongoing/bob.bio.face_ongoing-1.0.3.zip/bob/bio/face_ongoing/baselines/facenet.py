#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
from bob.bio.base.baseline import Baseline

preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")
preprocessors["mobio"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["lfw"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["arface"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["casia_webface"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/casia_webface_crop.py")

facenet = Baseline(name = "facenet",\
                    extractor = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/facenet_sandberg/inception_v1.py"),\
                    algorithm = 'distance-cosine',\
                    preprocessors=preprocessors)


facenet_5b = Baseline(name = "facenet_5b",\
                    extractor = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/casiawebface/inception_resnet_v2/centerloss_rgb_parts.py"),\
                    algorithm = 'distance-cosine',\
                    preprocessors=preprocessors)
 
