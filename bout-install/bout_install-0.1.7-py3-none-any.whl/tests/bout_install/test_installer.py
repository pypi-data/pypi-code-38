#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from bout_install.Installer import Installer
from tests.utils import BaseTestSetup


class TestInstall(unittest.TestCase):
    def setUp(self):
        """
        Set up global test parameters, and modify config.ini

        A back-up of config.ini is made prior to modification
        """

        self.base_setup = BaseTestSetup('install')
        self.base_setup.set_up()

        # Get the main dir and other dir
        self.main_dir = self.base_setup.main_dir
        self.other_dir = self.base_setup.other_dir

        # Setup the config path
        self.config = self.base_setup.test_config_ini_path

        # Get the fftw url
        fftw_version = self.base_setup.config['versions']['fftw']
        self.fftw_url = f'http://www.fftw.org/fftw-{fftw_version}.tar.gz'

        self.installer = Installer(config_path=self.config)

    def tearDown(self):
        """
        Remove created directories and files, restore config.ini
        """

        self.base_setup.tear_down()

    def test__setup_logger(self):
        """
        Test that the logger is working
        """

        log_path = self.main_dir.joinpath('test.log')
        installer = Installer(config_path=self.config,
                              log_path=log_path)
        installer.logger.info('This is a test')
        self.assertTrue(log_path.is_file())

    def test_set_install_dirs(self):
        """
        Tests that the directories are properly installed
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        install_dir = self.main_dir.joinpath('install')
        local_dir = self.main_dir.joinpath('local')
        examples_dir = self.main_dir.joinpath('examples')
        self.assertTrue(install_dir.is_dir())
        self.assertTrue(local_dir.is_dir())
        self.assertTrue(examples_dir.is_dir())

        install_dir = self.other_dir.joinpath('install')
        local_dir = self.other_dir.joinpath('local')
        examples_dir = self.other_dir.joinpath('examples')
        self.installer.setup_install_dirs(install_dir=install_dir,
                                          local_dir=local_dir,
                                          examples_dir=examples_dir)
        self.assertTrue(install_dir.is_dir())
        self.assertTrue(local_dir.is_dir())
        self.assertTrue(examples_dir.is_dir())

    def test_get_tar_file(self):
        """
        Tests that the .tar files can be downloaded
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        tar_file_path = \
            self.installer.get_tar_file_path(url=self.fftw_url)

        self.installer.get_tar_file(url=self.fftw_url)
        self.assertTrue(tar_file_path.is_file())

    def test_untar(self):
        """
        Tests for successful untaring
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        tar_file_path = \
            self.installer.get_tar_file_path(url=self.fftw_url)

        self.installer.get_tar_file(url=self.fftw_url)
        self.installer.untar(tar_file_path)

        tar_dir = self.installer.get_tar_dir(tar_file_path)
        self.assertTrue(tar_dir.is_dir())

    def test_configure(self):
        """
        Test for successful configuring
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        tar_file_path = \
            self.installer.get_tar_file_path(url=self.fftw_url)
        self.installer.get_tar_file(url=self.fftw_url)

        self.installer.untar(tar_file_path)

        config_options = dict(prefix=str(self.installer.local_dir))
        config_str = \
            self.installer.get_configure_command(config_options=config_options)

        tar_dir = self.installer.get_tar_dir(tar_file_path)
        self.installer.run_subprocess(config_str, tar_dir)
        self.assertTrue(tar_dir.joinpath('config.log').is_file())

    def test_make(self):
        """
        Test for successful making
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        tar_file_path = \
            self.installer.get_tar_file_path(url=self.fftw_url)

        self.installer.get_tar_file(url=self.fftw_url)
        self.installer.untar(tar_file_path)

        config_options = dict(prefix=str(self.installer.local_dir))
        config_str = \
            self.installer.get_configure_command(config_options=config_options)

        tar_dir = self.installer.get_tar_dir(tar_file_path)
        self.installer.run_subprocess(config_str, tar_dir)
        self.installer.make(tar_dir)
        bin_file = self.installer.local_dir.joinpath('bin', 'fftw-wisdom')
        self.assertTrue(bin_file.is_file())

    def test_install_package(self):
        """
        Tests that the install wrapper is working
        """

        self.installer.setup_install_dirs(main_dir=self.main_dir)
        bin_file = self.installer.local_dir.joinpath('bin', 'fftw-wisdom')
        self.installer.install_package(self.fftw_url, bin_file)
        self.assertTrue(bin_file.is_file())


if __name__ == '__main__':
    unittest.main()

