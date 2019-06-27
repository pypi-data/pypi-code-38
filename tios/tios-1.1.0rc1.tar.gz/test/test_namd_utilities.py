import unittest
from tios import namd_utilities
import tempfile
import os
import zlib

class TestNAMDUtilitiesMethods(unittest.TestCase):

    def test_config_file_valid_for_imd(self):
        configfile = 'test/examples/ubq_wb.conf'
        self.assertTrue(namd_utilities.config_file_valid_for_imd(configfile))

    def test_config_file_does_not_set_imd(self):
        configfile = 'test/examples/ubq_wb_no_imd.conf'
        self.assertFalse(namd_utilities.config_file_valid_for_imd(configfile))

    def test_config_file_is_NPT(self):
        configfile = 'test/examples/ubq_wb_NPT.conf'
        self.assertFalse(namd_utilities.config_file_valid_for_imd(configfile))

    def test_dt_from_config_file(self):
        configfile = 'test/examples/ubq_wb.conf'
        dt = namd_utilities.dt_from_config_file(configfile)
        self.assertEqual(dt, 0.002)

    def test_trate_from_config_file(self):
        configfile = 'test/examples/ubq_wb.conf'
        trate = namd_utilities.trate_from_config_file(configfile)
        self.assertEqual(trate, 500)

    def test_filenames_from_config_file(self):
        configfile = 'test/examples/ubq_wb.conf'
        filenames = namd_utilities.filenames_from_config_file(configfile)
        expected_filenames = ['test/examples/ubq_wb.psf', 
                              'test/examples/ubq_wb.pdb', 
                              'test/examples/ubq_wb_eq.coor', 
                              'test/examples/ubq_wb_eq.xsc', 
                              'test/examples/ubq_wb.conf', 
                              'test/examples/par_all27_prot_lipid.inp']
        #self.assertItemsEqual(filenames, expected_filenames)
        for f in expected_filenames:
            self.assertIn(f, filenames)
