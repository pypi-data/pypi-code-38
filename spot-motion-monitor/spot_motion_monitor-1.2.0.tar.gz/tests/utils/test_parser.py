#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.utils import create_parser

class TestArgumentParser():

    def setup_class(cls):
        cls.parser = create_parser()

    def test_objectAfterConstruction(self):
        assert self.parser is not None

    def test_helpDocumentation(self):
        assert self.parser.format_help() is not None

    def test_behaviorWithNoArguments(self):
        args = self.parser.parse_args([])
        assert args.profile is False
        assert args.config_file is None
        assert args.auto_run is False

    def test_profileFlag(self):
        args = self.parser.parse_args(['--profile'])
        assert args.profile is True

    def test_telemetryDirectory(self):
        telem_dir1 = '/test/it/out'
        telem_dir2 = '/another/to/try'
        args = self.parser.parse_args(['-t', telem_dir1])
        assert args.telemetry_dir == telem_dir1
        args = self.parser.parse_args(['--telemetry_dir', telem_dir2])
        assert args.telemetry_dir == telem_dir2

    def test_configFileFlag(self):
        conf_file1 = 'test.yaml'
        conf_file2 = 'another.yaml'
        args = self.parser.parse_args(['-c', conf_file1])
        assert args.config_file == conf_file1
        args = self.parser.parse_args(['--config', conf_file2])
        assert args.config_file == conf_file2

    def test_autoRunFlag(self):
        args = self.parser.parse_args(['-a'])
        assert args.auto_run is True
        args = self.parser.parse_args(['--auto_run'])
        assert args.auto_run is True

    def test_vimbaCameraIndex(self):
        args = self.parser.parse_args([])
        assert args.vimba_camera_index is None
        args = self.parser.parse_args(['-i', '1'])
        assert args.vimba_camera_index == 1
        args = self.parser.parse_args(['--camera-index', '2'])
        assert args.vimba_camera_index == 2
