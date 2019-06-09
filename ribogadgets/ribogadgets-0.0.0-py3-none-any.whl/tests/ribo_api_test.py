# -*- coding: utf-8 -*-
import unittest
import os

import pandas as pd
import h5py

from test_data import *
import ribogadgets
from ribogadgets import create
from ribogadgets.settings import *
from ribogadgets.ribo import ribo

###########################################
REF_LEN_FILE = "ref_lengths_api.tsv"
TEST_RIBO = "test_api.ribo"

###########################################

# TO be completed
"""
class TestRiboAPI(unittest.TestCase):

    def setUp(self):
        with open(REF_LEN_FILE, "w") as output_stream:
            print(TRANSCRIPT_LENGTHS, file=output_stream)
        create.create_ribo_file(TEST_RIBO, "api_exp_1", REF_LEN_FILE)
        self.ribo = ribo(TEST_RIBO)
        
    def tearDown(self):
        os.remove(REF_LEN_FILE)
        del self.ribo
        os.remove(TEST_RIBO)

    def test_experiments(self):
        self.assertIn("api_exp_1", self.ribo.experiments)
        self.assertNotIn("sherlock", self.ribo.experiments)
"""

if __name__ == '__main__':
        
    unittest.main()