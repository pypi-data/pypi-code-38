#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest
import os.path as op
import platform

path_to_script = op.dirname(op.abspath(__file__))

import sys

sys.path.insert(0, op.abspath(op.join(path_to_script, "../../io3d")))
sys.path.insert(0, op.abspath(op.join(path_to_script, "../../imma")))
# import sys
# import os.path

# imcut_path =  os.path.join(path_to_script, "../../imcut/")
# sys.path.insert(0, imcut_path)
import io3d
import scaffan
import scaffan.annotation

import glob
import os

skip_on_local = False


class ParseAnnotationTest(unittest.TestCase):
    @unittest.skipIf(
        platform.system() == "Windows",
        "On windows there is problem with openslides import. Test works standalone but not together with the others.",
    )
    def test_convert_annotation_hamamatsu_data(self):
        slices_dir = io3d.datasets.join_path("medical/orig/sample_data/SCP003/", get_root=True)

        json_files = glob.glob(op.join(slices_dir, "*.json"))
        for fn in json_files:
            os.remove(fn)

        scaffan.annotation.ndpa_to_json(slices_dir)

        json_files = glob.glob(op.join(slices_dir, "*.json"))

        self.assertGreater(len(json_files), 0)

    @unittest.skipIf(
        platform.system() == "Windows",
        "On windows there is problem with openslides import. Test works standalone but not together with the others.",
    )
    def test_convert_annotation_hamamatsu_data_single_file(self):
        # slices_dir = io3d.datasets.join_path("medical/orig/", get_root=True)
        fn = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi", get_root=True)
        # json_file = io3d.datasets.join_path("medical", "orig", "CMU-1.ndpi.ndpa.json", get_root=True)
        json_file = fn + ".ndpa.json"
        if op.exists(json_file):
            os.remove(json_file)

        scaffan.annotation.ndpa_to_json(fn)
        logger.debug(json_file)

        self.assertTrue(op.exists(json_file))

    # @unittest.skipIf(os.environ.get("TRAVIS", skip_on_local), "Skip on Travis-CI")
    @unittest.skipIf(
        platform.system() == "Windows",
        "On windows there is problem with openslides import. Test works standalone but not together with the others.",
    )
    def test_convert_annotation_scaffold_data(self):
        slices_dir = io3d.datasets.join_path(
            "medical", "orig", "sample_data", "SCP003", get_root=True
        )

        json_files = glob.glob(op.join(slices_dir, "*.json"))
        for fn in json_files:
            os.remove(fn)

        scaffan.annotation.ndpa_to_json(slices_dir)

        json_files = glob.glob(op.join(slices_dir, "*.json"))

        self.assertGreater(len(json_files), 0)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr)
    # logger.setLevel(logging.DEBUG)
    unittest.main()
