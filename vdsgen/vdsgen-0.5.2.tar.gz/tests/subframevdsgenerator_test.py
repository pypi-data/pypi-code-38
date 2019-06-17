import os
import sys
import unittest
from mock import MagicMock, patch, call

from vdsgen import vdsgenerator
from vdsgen.subframevdsgenerator import SubFrameVDSGenerator

vdsgen_patch_path = "vdsgen.subframevdsgenerator"
VDSGenerator_patch_path = vdsgen_patch_path + ".VDSGenerator"
h5py_patch_path = "h5py"

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "h5py"))


class SubFrameVDSGeneratorTester(SubFrameVDSGenerator):
    """A version of SubFrameVDSGenerator without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)
        self.logger = MagicMock()


class SubFrameVDSGeneratorInitTest(unittest.TestCase):

    @patch(VDSGenerator_patch_path + '.__init__')
    def test_super_called(self, super_mock):
        SubFrameVDSGenerator("/test/path", prefix="stripe_")

        super_mock.assert_called_once_with("/test/path", "stripe_",
                                           *[None]*7)


class SimpleFunctionsTest(unittest.TestCase):

    @patch(VDSGenerator_patch_path + '.grab_metadata',
           return_value=dict(frames=(3,), height=256, width=2048,
                             dtype="uint16"))
    def test_process_source_datasets_given_valid_data(self, grab_mock):
        gen = SubFrameVDSGeneratorTester(
            files=["stripe_1.h5", "stripe_2.h5"])
        expected_source = vdsgenerator.SourceMeta(
            frames=(3,), height=256, width=2048, dtype="uint16")

        source = gen.process_source_datasets()

        grab_mock.assert_has_calls([call("stripe_1.h5"), call("stripe_2.h5")])
        self.assertEqual(expected_source, source)

    @patch(VDSGenerator_patch_path + '.grab_metadata',
           side_effect=[dict(frames=3, height=256, width=2048, dtype="uint16"),
                        dict(frames=4, height=256, width=2048,
                             dtype="uint16")])
    def test_process_source_datasets_given_mismatched_data(self, grab_mock):
        gen = SubFrameVDSGeneratorTester(
            files=["stripe_1.h5", "stripe_2.h5"])

        with self.assertRaises(ValueError):
            gen.process_source_datasets()

        grab_mock.assert_has_calls([call("stripe_1.h5"), call("stripe_2.h5")])

    def test_construct_vds_spacing(self):
        gen = SubFrameVDSGeneratorTester(
            files=[""] * 6, stripe_spacing=10, module_spacing=100)
        expected_spacing = [10, 100, 10, 100, 10, 0]

        spacing = gen.construct_vds_spacing()

        self.assertEqual(expected_spacing, spacing)

    file_mock = MagicMock()

    @patch(h5py_patch_path + '.File', return_value=file_mock)
    @patch(h5py_patch_path + '.VirtualSource')
    @patch(h5py_patch_path + '.VirtualLayout')
    def test_create_virtual_layout(self, layout_mock, source_mock, file_mock):
        gen = SubFrameVDSGeneratorTester(
            output_file="/test/path/vds.hdf5",
            stripe_spacing=10, module_spacing=100,
            target_node="full_frame", source_node="data",
            files=["raw1.h5", "raw2.h5", "raw3.h5",
                   "raw4.h5", "raw5.h5", "raw6.h5"],
            name="vds.hdf5")
        source = vdsgenerator.SourceMeta(
            frames=(3,), height=256, width=2048, dtype="uint16")
        dataset_mock = MagicMock()
        self.file_mock.reset_mock()
        vds_file_mock = self.file_mock.__enter__.return_value
        vds_file_mock.__getitem__.return_value = dataset_mock

        layout = gen.create_virtual_layout(source)

        layout_mock.assert_called_once_with((3, 1766, 2048), "uint16")
        source_mock.assert_has_calls(
            [call("raw{}.h5".format(x),
                  dtype="uint16", name="data", shape=(3, 256, 2048))
             for x in range(1, 7)])
        # TODO: Pass numpy arrays to check slicing
