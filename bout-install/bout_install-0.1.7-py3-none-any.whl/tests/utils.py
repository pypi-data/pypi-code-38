#!/usr/bin/env python
# -*- coding: utf-8 -*-


import shutil
import configparser
from pathlib import Path


class BaseTestSetup(object):
    """
    A class for facilitating the set up and tear down of the tests
    """

    def __init__(self, test_name):
        """
        Sets the paths and the path name

        Parameters
        ----------
        test_name : str
            The name of the test (in order to not get concurrency issues as
            tests are run in parallel)
        """
        root_dir = Path(__file__).absolute().parents[1]

        self.main_dir = root_dir.joinpath(f'test_main_dir_{test_name}')
        self.other_dir = root_dir.joinpath(f'test_other_dir_{test_name}')
        self.config_ini_path = root_dir.joinpath('bout_install', 'config.ini')
        self.test_config_ini_path = \
            self.config_ini_path.parent.joinpath(f'config_{test_name}.ini')

        # Initialize
        self.config = None

    def set_up(self):
        """
        Copy and modify the original config.ini
        """

        # Copy the content of config.ini
        shutil.copy(self.config_ini_path, self.test_config_ini_path)

        # Replace the main_dir
        self.config = configparser.ConfigParser(allow_no_value=True)
        with self.test_config_ini_path.open() as f:
            self.config.read_file(f)

        self.config['install_options']['main_dir'] = str(self.main_dir)
        self.config['bout_options']['git_dir'] = \
            str(self.main_dir.joinpath('BOUT-dev'))
        with self.test_config_ini_path.open('w') as f:
            self.config.write(f)

    def tear_down(self):
        """
        Remove created directories and files, restore config.ini
        """

        shutil.rmtree(self.main_dir, ignore_errors=True)
        shutil.rmtree(self.other_dir, ignore_errors=True)
        self.test_config_ini_path.unlink()
