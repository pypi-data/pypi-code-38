#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


import pkg_resources
from bob.bio.base.baseline import Baseline

preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/drgan/default_crop.py")
preprocessors["mobio"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/drgan/eyes_crop.py")
preprocessors["lfw"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/drgan/eyes_crop.py")
drgan = Baseline(name = "drgan",\
                    algorithm = 'distance-cosine',\
                    extractor = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/drgan/extractor.py"),\
                    preprocessors=preprocessors)
