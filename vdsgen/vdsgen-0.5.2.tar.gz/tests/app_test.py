import unittest
from mock import MagicMock, patch, call

from vdsgen import app

app_patch_path = "vdsgen.app"
parser_patch_path = app_patch_path + ".ArgumentParser"
VDSGenerator_patch_path = app_patch_path + ".VDSGenerator"
InterleaveVDSGenerator_patch_path = app_patch_path + ".InterleaveVDSGenerator"
SubFrameVDSGenerator_patch_path = app_patch_path + ".SubFrameVDSGenerator"
ExcaliburGapFillVDSGenerator_patch_path = app_patch_path + \
                                          ".ExcaliburGapFillVDSGenerator"
ReshapeVDSGenerator_patch_path = app_patch_path + \
                                 ".ReshapeVDSGenerator"


class ParseArgsTest(unittest.TestCase):

    @patch(parser_patch_path + '.error')
    @patch(parser_patch_path + '.parse_args',
           return_value=MagicMock(empty=True, files=None))
    def test_empty_and_not_files_then_error(self, parse_mock, error_mock):

        app.parse_args()

        parse_mock.assert_called_once_with()
        error_mock.assert_called_once_with(
            "To make an empty VDS you must explicitly define --files for the "
            "eventual raw datasets.")

    @patch(parser_patch_path + '.error')
    @patch(parser_patch_path + '.parse_args',
           return_value=MagicMock(mode="gap-fill", files=["one.h5", "two.h5"]))
    def test_gap_fill_only_one_file(self, parse_mock, error_mock):

        app.parse_args()

        parse_mock.assert_called_once_with()
        error_mock.assert_called_once_with(
            "Gap fill can only operate on a single dataset.")


class MainTest(unittest.TestCase):

    @patch(SubFrameVDSGenerator_patch_path)
    @patch(app_patch_path + '.parse_args',
           return_value=MagicMock(mode="sub-frames", empty=True))
    def test_main_empty(self, parse_mock, init_mock):
        gen_mock = init_mock.return_value
        args_mock = parse_mock.return_value

        app.main()

        parse_mock.assert_called_once_with()
        init_mock.assert_called_once_with(
            args_mock.path,
            prefix=args_mock.prefix, files=args_mock.files,
            output=args_mock.output,
            source=dict(shape=args_mock.shape, dtype=args_mock.data_type),
            source_node=args_mock.source_node,
            target_node=args_mock.target_node,
            stripe_spacing=args_mock.stripe_spacing,
            module_spacing=args_mock.module_spacing,
            fill_value=args_mock.fill_value,
            log_level=args_mock.log_level)

        gen_mock.generate_vds.assert_called_once_with()

    @patch(SubFrameVDSGenerator_patch_path)
    @patch(app_patch_path + '.parse_args',
           return_value=MagicMock(mode="sub-frames", empty=False))
    def test_main_not_empty(self, parse_mock, init_mock):
        args_mock = parse_mock.return_value

        app.main()

        parse_mock.assert_called_once_with()
        init_mock.assert_called_once_with(
            args_mock.path,
            prefix=args_mock.prefix, files=args_mock.files,
            output=args_mock.output,
            source=None,
            source_node=args_mock.source_node,
            target_node=args_mock.target_node,
            stripe_spacing=args_mock.stripe_spacing,
            module_spacing=args_mock.module_spacing,
            fill_value=args_mock.fill_value,
            log_level=args_mock.log_level)

    @patch(InterleaveVDSGenerator_patch_path)
    @patch(app_patch_path + '.parse_args',
           return_value=MagicMock(mode="interleave", empty=False))
    def test_main_interleave(self, parse_mock, init_mock):
        args_mock = parse_mock.return_value

        app.main()

        parse_mock.assert_called_once_with()
        init_mock.assert_called_once_with(
            args_mock.path,
            prefix=args_mock.prefix, files=args_mock.files,
            output=args_mock.output,
            source=None,
            source_node=args_mock.source_node,
            target_node=args_mock.target_node,
            block_size=args_mock.block_size,
            fill_value=args_mock.fill_value,
            log_level=args_mock.log_level)

    @patch(ExcaliburGapFillVDSGenerator_patch_path)
    @patch(app_patch_path + '.parse_args',
           return_value=MagicMock(mode="gap-fill", modules=3, empty=False))
    def test_main_gap_fill(self, parse_mock, init_mock):
        args_mock = parse_mock.return_value

        app.main()

        parse_mock.assert_called_once_with()
        init_mock.assert_called_once_with(
            args_mock.path,
            prefix=args_mock.prefix, files=args_mock.files,
            output=args_mock.output,
            source=None,
            source_node=args_mock.source_node,
            target_node=args_mock.target_node,
            modules=args_mock.modules,
            chip_spacing=args_mock.stripe_spacing,
            module_spacing=args_mock.module_spacing,
            fill_value=args_mock.fill_value,
            log_level=args_mock.log_level)

    @patch(ReshapeVDSGenerator_patch_path)
    @patch(app_patch_path + '.parse_args',
           return_value=MagicMock(mode="reshape", empty=False))
    def test_main_reshape(self, parse_mock, init_mock):
        args_mock = parse_mock.return_value

        app.main()

        parse_mock.assert_called_once_with()
        init_mock.assert_called_once_with(
            tuple(args_mock.new_shape),
            args_mock.path,
            prefix=args_mock.prefix, files=args_mock.files,
            output=args_mock.output,
            source=None,
            source_node=args_mock.source_node,
            target_node=args_mock.target_node,
            fill_value=args_mock.fill_value,
            log_level=args_mock.log_level,
            alternate=args_mock.alternate
        )
