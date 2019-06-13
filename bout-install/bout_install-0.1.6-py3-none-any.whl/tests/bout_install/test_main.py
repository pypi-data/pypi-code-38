#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import unittest
import shutil
import subprocess
from pathlib import Path
from bout_install.main import install_bout
from bout_install.main import add_str_to_bashrc
from tests.utils import BaseTestSetup


class TestMain(unittest.TestCase):
    def setUp(self):
        """
        Set up global test parameters, and modify config.ini

        A back-up of config.ini is made prior to modification
        """

        self.base_setup = BaseTestSetup('boutpp')
        self.base_setup.set_up()

        # Setup the config path
        self.config = self.base_setup.test_config_ini_path

    def tearDown(self):
        """
        Remove created directories and files, restore config.ini
        """

        self.base_setup.tear_down()

    def test_main(self):
        """
        Test the installation and that we can run blob2d with PETSc
        """

        install_bout(self.config)

        # We now try to make blob 2d
        # The os.environ from BOUTPPInstaller should persist, so no need of
        # running it again

        # Copy to data/
        blob2d_dir = self.base_setup.main_dir.joinpath('BOUT-dev',
                                                       'examples',
                                                       'blob2d')
        data_dir = blob2d_dir.joinpath('data')
        delta_025_dir = blob2d_dir.joinpath('delta_0.25')
        shutil.copytree(delta_025_dir, data_dir)

        # Change BOUT.inp lines
        n_out = re.compile(r'^\bNOUT\b', re.IGNORECASE)
        time_step = re.compile(r'^\bTIMESTEP\b', re.IGNORECASE)
        boussinesq = re.compile(r'^\bboussinesq\b', re.IGNORECASE)

        bout_inp_path = data_dir.joinpath('BOUT.inp')
        with bout_inp_path.open('r') as f:
            bout_inp_list = f.readlines()
            for i in range(len(bout_inp_list)):
                if n_out.search(bout_inp_list[i]):
                    bout_inp_list[i] = 'NOUT = 2\n'
                elif time_step.search(bout_inp_list[i]):
                    bout_inp_list[i] = 'TIMESTEP = 1e-5\n'
                elif boussinesq.search(bout_inp_list[i]):
                    bout_inp_list[i] = 'boussinesq = false\n'

        with bout_inp_path.open('w') as f:
            f.writelines(bout_inp_list)

        # Make
        command = 'make'
        result = subprocess.run(command.split(),
                                cwd=blob2d_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        result.check_returncode()

        # Run
        command = 'mpirun -np 2 ./blob2d'
        result = subprocess.run(command.split(),
                                cwd=blob2d_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        result.check_returncode()


class TestMainHelpers(unittest.TestCase):
    def setUp(self):
        """
        Make a backup of .bashrc (makes the file if it doesn't exist)
        """

        self.bashrc_path = Path.home().joinpath('.bashrc')
        self.exist = self.bashrc_path.is_file()
        if not self.exist:
            self.bashrc_path.touch()

        self.bashrc_bak_path = Path.home().joinpath('.bashrc.bak')
        shutil.copy(self.bashrc_path, self.bashrc_bak_path)

    def tearDown(self):
        """
        Move .bashrc.bak to .bashrc
        """

        shutil.copy(self.bashrc_bak_path, self.bashrc_path)
        self.bashrc_bak_path.unlink()

        if not self.exist:
            self.bashrc_path.unlink()

    def test_add_str_to_bashrc(self):
        """
        Test that we can add to bashrc
        """

        expected = '# harmless string'
        add_str_to_bashrc(expected)

        with self.bashrc_path.open('r') as f:
            lines = f.readlines()

        self.assertEqual(expected, lines[-1])


if __name__ == '__main__':
    unittest.main()

