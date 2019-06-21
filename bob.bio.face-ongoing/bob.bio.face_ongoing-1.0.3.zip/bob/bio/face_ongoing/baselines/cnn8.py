#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


import pkg_resources
from bob.bio.base.baseline import Baseline

preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/cnn8/default_crop.py")
preprocessors["mobio"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/cnn8/eyes_crop.py")
preprocessors["lfw"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/cnn8/eyes_crop.py")

cnn8 = Baseline(name = "cnn8", \
                algorithm = 'distance-cosine', \
                preprocessors=preprocessors, \
                extractor=pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/cnn8/extractor.py"))
