import os
import sys
import unittest
from mock import MagicMock, patch, call

from vdsgen import vdsgenerator
from vdsgen.gapfillvdsgenerator import GapFillVDSGenerator

vdsgen_patch_path = "vdsgen.gapfillvdsgenerator"
VDSGenerator_patch_path = vdsgen_patch_path + ".VDSGenerator"
h5py_patch_path = "h5py"

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "h5py"))


class GapFillVDSGeneratorTester(GapFillVDSGenerator):
    """A version of GapFillVDSGenerator without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)
        self.logger = MagicMock()


class GapFillVDSGeneratorInitTest(unittest.TestCase):

    super_mock = MagicMock()

    def set_files(self, _path, _prefix, files, *_):
        """A method to patch VDSGenerator __init__ with"""
        # Set self.files so the GapFill __init__ works
        self.files = files
        # Make a call we can test for
        GapFillVDSGeneratorInitTest.super_mock(_path, _prefix, files, *_)

    @classmethod
    def setUp(cls):
        cls.super_mock.reset_mock()

    @patch(VDSGenerator_patch_path + '.__init__', new=set_files)
    def test_init(self):
        GapFillVDSGenerator("/test/path", files=["raw.h5"])

        self.super_mock.assert_called_once_with(
            "/test/path", None, ["raw.h5"], *[None]*6)

    @patch(VDSGenerator_patch_path + '.__init__', new=set_files)
    def test_init_given_more_than_one_file_then_error(self):
        self.assertRaises(ValueError,
                          GapFillVDSGenerator,
                          "/test/path", files=["raw_1.h5", "raw_2.h5"])


class SimpleFunctionsTest(unittest.TestCase):

    @patch(VDSGenerator_patch_path + '.grab_metadata',
           return_value=dict(frames=(3,), height=256, width=2048,
                             dtype="uint16"))
    def test_process_source_datasets_given_valid_data(self, grab_mock):
        gen = GapFillVDSGeneratorTester(
            files=["raw.h5"])
        expected_source = vdsgenerator.SourceMeta(
            frames=(3,), height=256, width=2048, dtype="uint16")

        source = gen.process_source_datasets()

        grab_mock.assert_called_once_with("raw.h5")
        self.assertEqual(expected_source, source)

    def test_construct_vds_spacing(self):
        gen = GapFillVDSGeneratorTester()

        with self.assertRaises(NotImplementedError):
            gen.construct_vds_spacing()

    def test_create_virtual_layout(self):
        gen = GapFillVDSGeneratorTester()

        with self.assertRaises(NotImplementedError):
            gen.create_virtual_layout(MagicMock())
