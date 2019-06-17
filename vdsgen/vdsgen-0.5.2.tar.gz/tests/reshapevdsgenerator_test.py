import os
import sys
import unittest
from mock import MagicMock, patch, call

from vdsgen import vdsgenerator
from vdsgen.reshapevdsgenerator import ReshapeVDSGenerator

vdsgen_patch_path = "vdsgen.reshapevdsgenerator"
VDSGenerator_patch_path = vdsgen_patch_path + ".VDSGenerator"
Reshape_patch_path = vdsgen_patch_path + ".ReshapeVDSGenerator"
h5py_patch_path = "h5py"

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "h5py"))


class ReshapeVDSGeneratorTester(ReshapeVDSGenerator):
    """A version of VDSGenerator without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class ReshapeVDSGeneratorInitTest(unittest.TestCase):

    super_mock = MagicMock()

    def set_files(self, _path, _prefix, files, *_):
        """A method to patch VDSGenerator __init__ with"""
        # Set self.files so the GapFill __init__ works
        self.files = files
        # Make a call we can test for
        ReshapeVDSGeneratorInitTest.super_mock(_path, _prefix, files, *_)

    @classmethod
    def setUp(cls):
        cls.super_mock.reset_mock()

    @patch(VDSGenerator_patch_path + ".__init__", new=set_files)
    def test_super_called(self):
        ReshapeVDSGenerator((3, 5, 10), "/test/path", files=["raw.h5"])

        self.super_mock.assert_called_once_with("/test/path", None, ["raw.h5"],
                                                *[None]*6)


class SimpleFunctionsTest(unittest.TestCase):

    @patch(VDSGenerator_patch_path + ".grab_metadata",
           return_value=dict(frames=(5,), height=256, width=2048,
                             dtype="uint16"))
    def test_process_source_datasets_given_valid_data(self, grab_mock):
        gen = ReshapeVDSGeneratorTester(
            files=["raw.h5"])
        expected_source = vdsgenerator.SourceMeta(
            frames=(5,), height=256, width=2048, dtype="uint16")

        source = gen.process_source_datasets()

        grab_mock.assert_called_once_with("raw.h5")
        self.assertEqual(expected_source, source)

    @patch(VDSGenerator_patch_path + ".grab_metadata",
           side_effect=[
               dict(frames=(3,), height=256, width=2048, dtype="uint16"),
               dict(frames=(3,), height=512, width=2048, dtype="uint16")])
    def test_process_source_datasets_given_mismatched_data(self, grab_mock):
        gen = ReshapeVDSGeneratorTester(
            files=["stripe_1.h5", "stripe_2.h5"])

        with self.assertRaises(ValueError):
            gen.process_source_datasets()

        grab_mock.assert_has_calls([call("stripe_1.h5"), call("stripe_2.h5")])

    file_mock = MagicMock()

    @patch(vdsgen_patch_path + '.VirtualSource')
    @patch(vdsgen_patch_path + '.VirtualLayout')
    def test_create_virtual_layout(self, layout_mock, source_mock):
        gen = ReshapeVDSGeneratorTester(
            output_file="/test/path/vds.hdf5",
            dimensions=(5, 3, 10), alternate=None, periods=[], radices=(30, 10),
            target_node="full_frame", source_node="data",
            source_file="raw.h5", name="vds.hdf5")
        source = vdsgenerator.SourceMeta(
            frames=(150,), height=256, width=2048, dtype="uint16")
        dataset_mock = MagicMock()
        self.file_mock.reset_mock()
        vds_file_mock = self.file_mock.__enter__.return_value
        vds_file_mock.__getitem__.return_value = dataset_mock

        gen.create_virtual_layout(source)

        layout_mock.assert_called_once_with((5, 3, 10, 256, 2048), "uint16")
        source_mock.assert_called_once_with(
            "raw.h5", dtype="uint16", name="data", shape=(150, 256, 2048)
        )

    @patch(vdsgen_patch_path + '.VirtualSource')
    @patch(vdsgen_patch_path + '.VirtualLayout')
    @patch(Reshape_patch_path + ".create_alternating_virtual_layout")
    def test_create_virtual_layout_calls_alternating(self, alt_mock,
                                                     layout_mock, source_mock):
        gen = ReshapeVDSGeneratorTester(
            dimensions=(5, 3, 10), alternate=(False, True),
            source_node="data",
            source_file="raw.h5")
        source = vdsgenerator.SourceMeta(
            frames=(150,), height=256, width=2048, dtype="uint16")

        gen.create_virtual_layout(source)

        alt_mock.assert_called_once_with(
            source_mock.return_value, layout_mock.return_value
        )

    def test_create_virtual_layout_frame_mismatch(self):
        gen = ReshapeVDSGeneratorTester(
            output_file="/test/path/vds.hdf5",
            dimensions=(5, 3, 10), alternate=None, periods=[], radices=(30, 10),
            target_node="full_frame", source_node="data",
            source_file="raw.h5", name="vds.hdf5")
        source = vdsgenerator.SourceMeta(
            frames=(3,), height=256, width=2048, dtype="uint16")

        with self.assertRaises(ValueError):
            gen.create_virtual_layout(source)

    @patch(Reshape_patch_path + "._calculate_axis_indices")
    @patch(Reshape_patch_path + "._create_mixed_radix_set")
    def test_create_alternating_virtual_layout(self, radix_mock, calculate_mock):
        gen = ReshapeVDSGeneratorTester(
            output_file="/test/path/vds.hdf5",
            dimensions=(5, 3, 10), alternate=[False, True, True], radices=(30, 10),
            target_node="full_frame", source_node="data",
            source_file="raw.h5", name="vds.hdf5")

        v_source_mock = MagicMock()
        v_layout_mock = MagicMock()

        gen.create_alternating_virtual_layout(v_source_mock, v_layout_mock)

        radix_mock.assert_called_once_with()
        for i in range(150):
            # Need to ignore call().__add__() etc. calls
            calculate_mock.assert_any_call(i, radix_mock.return_value)

        v_source_mock.__getitem__.assert_has_calls(
            [call(i) for i in range(150)]
        )
        v_layout_mock.__setitem__.assert_has_calls(
            [call((), v_source_mock.__getitem__.return_value)] * 150
        )

    def test_create_mixed_radix_set(self):
        gen = ReshapeVDSGeneratorTester(dimensions=(5, 3, 10))
        expected_radix = (30, 10, 1)

        radix = gen._create_mixed_radix_set()

        self.assertEqual(expected_radix, radix)

    def test_calculate_reshaped_indices(self):
        gen = ReshapeVDSGeneratorTester(
            dimensions=(5, 3, 10), alternate=(False, False, False)
        )

        expected_indices = [1, 1, 2]
        indices = gen._calculate_axis_indices(42, (30, 10, 1))
        self.assertEqual(expected_indices, indices)

        expected_indices = [4, 1, 0]
        indices = gen._calculate_axis_indices(130, (30, 10, 1))
        self.assertEqual(expected_indices, indices)

    def test_calculate_reshaped_indices_alternating(self):
        gen = ReshapeVDSGeneratorTester(
            dimensions=(5, 3, 10), alternate=(False, True, True)
        )

        expected_indices = [1, 1, 2]
        indices = gen._calculate_axis_indices(42, (30, 10, 1))
        self.assertEqual(expected_indices, indices)

        expected_indices = [4, 1, 9]
        indices = gen._calculate_axis_indices(130, (30, 10, 1))
        self.assertEqual(expected_indices, indices)
