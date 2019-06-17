import os
import sys
import unittest
from mock import MagicMock, patch, call

from vdsgen import vdsgenerator
from vdsgen.excaliburgapfillvdsgenerator import ExcaliburGapFillVDSGenerator

vdsgen_patch_path = "vdsgen.excaliburgapfillvdsgenerator"
gapfill_vdsgen_patch_path = "vdsgen.gapfillvdsgenerator"
GapFillVDSGenerator_patch_path = vdsgen_patch_path + ".GapFillVDSGenerator"
h5py_patch_path = "h5py"

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "h5py"))


class ExcaliburGapFillVDSGeneratorTester(ExcaliburGapFillVDSGenerator):
    """A version of ExcaliburGapFillVDSGenerator without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)
        self.logger = MagicMock()


class ExcaliburGapFillVDSGeneratorInitTest(unittest.TestCase):

    @patch(GapFillVDSGenerator_patch_path + '.__init__')
    def test_super_called(self, super_mock):
        ExcaliburGapFillVDSGenerator("/test/path", files=["raw.h5"])

        super_mock.assert_called_once_with(
            "/test/path", None, ["raw.h5"], None, None, None, None, None,
            256, 256, 8, 2, None)


class SimpleFunctionsTest(unittest.TestCase):

    @patch(GapFillVDSGenerator_patch_path + '.grab_metadata',
           return_value=dict(frames=(3,), height=256, width=2048,
                             dtype="uint16"))
    def test_process_source_datasets_given_valid_data(self, grab_mock):
        gen = ExcaliburGapFillVDSGeneratorTester(
            files=["raw.h5"])
        expected_source = vdsgenerator.SourceMeta(
            frames=(3,), height=256, width=2048, dtype="uint16")

        source = gen.process_source_datasets()

        grab_mock.assert_called_once_with("raw.h5")
        self.assertEqual(expected_source, source)

    def test_construct_vds_spacing(self):
        gen = ExcaliburGapFillVDSGeneratorTester(
            files=[""] * 6,
            grid_x=8, grid_y=6, chip_spacing=10, module_spacing=100)
        expected_x_spacing = [10, 10, 10, 10, 10, 10, 10, 0]
        expected_y_spacing = [10, 100, 10, 100, 10, 0]

        x_spacing, y_spacing = gen.construct_vds_spacing()

        self.assertEqual(expected_x_spacing, x_spacing)
        self.assertEqual(expected_y_spacing, y_spacing)

    file_mock = MagicMock()

    @patch(vdsgen_patch_path +
           '.ExcaliburGapFillVDSGenerator.construct_vds_spacing',
           return_value=([3, 3, 3, 3, 3, 3, 3, 0], [3, 123, 3, 123, 3, 0]))
    @patch(h5py_patch_path + '.File', return_value=file_mock)
    @patch(gapfill_vdsgen_patch_path + '.VirtualSource')
    @patch(gapfill_vdsgen_patch_path + '.VirtualLayout')
    def test_create_virtual_layout(self, layout_mock, source_mock, file_mock,
                                   construct_mock):
        gen = ExcaliburGapFillVDSGeneratorTester(
            output_file="/test/path/vds.h5",
            grid_x=8, grid_y=6, sub_height=256, sub_width=256,
            source_node="data", target_node="full_frame",
            source_file="raw.h5", name="gaps.h5")
        source = vdsgenerator.SourceMeta(
            frames=(3,), height=1536, width=2048, dtype="uint16")
        dataset_mock = MagicMock()
        self.file_mock.reset_mock()
        vds_file_mock = self.file_mock.__enter__.return_value
        vds_file_mock.__getitem__.return_value = dataset_mock

        layout = gen.create_virtual_layout(source)

        layout_mock.assert_called_once_with((3, 1791, 2069), "uint16")
        source_mock.assert_called_once_with(
            "raw.h5", name="data", dtype="uint16", shape=(3, 1536, 2048))
        # TODO: Pass numpy arrays to check slicing
