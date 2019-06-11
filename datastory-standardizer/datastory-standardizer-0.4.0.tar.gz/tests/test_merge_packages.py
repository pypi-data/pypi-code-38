import os
import shutil
import unittest
import standardizer as sd


class TestMergePackages(unittest.TestCase):
    def setUp(self):
        self.testdir = os.path.dirname(os.path.abspath(__file__))
        self.destdir = os.path.join(self.testdir, "testdir")
        packages = (
            os.path.join(self.testdir, "testddf1"),
            os.path.join(self.testdir, "testddf2"),
        )
        sd.merge_packages(packages, self.destdir)

    def test_destdir_was_created(self):
        self.assertTrue(os.path.exists(self.destdir))

    def test_package_json_was_created(self):
        path = os.path.join(self.destdir, "datapackage.json")
        self.assertTrue(os.path.exists(path))

    def test_concepts_file_was_created(self):
        path = os.path.join(self.destdir, "ddf--concepts.csv")
        self.assertTrue(os.path.exists(path))

    def tearDown(self):
        shutil.rmtree(self.destdir)
