#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest
import os.path as op
# from nose.plugins.attrib import attr

path_to_script = op.dirname(op.abspath(__file__))

import sys

sys.path.insert(0, op.abspath(op.join(path_to_script, "../../io3d")))
sys.path.insert(0, op.abspath(op.join(path_to_script, "../../imma")))
# import sys
# import os.path

# imcut_path =  os.path.join(path_to_script, "../../imcut/")
# sys.path.insert(0, imcut_path)
import numpy as np
import io3d
import scaffan
import scaffan.annotation
import scaffan.annotation as scan

import glob
import os

import scaffan.image as scim
scim.import_openslide()
import openslide

skip_on_local = False


class ProcessJsonAnnotationTest(unittest.TestCase):

    def test_read_annotations(self):
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        imsl = openslide.OpenSlide(fn)
        annotations = scan.read_annotations(fn)
        scan.annotations_to_px(imsl, annotations)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr)
    logger.setLevel(logging.DEBUG)
    unittest.main()
