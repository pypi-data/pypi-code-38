# -*- coding: utf-8 -*-
import unittest
import os
from io import StringIO
import subprocess

import numpy as np
import h5py

from ribogadgets import create
from ribogadgets.core.coverage import find_coverage
from ribogadgets.core.get_gadgets import get_reference_names,\
                                         get_reference_lengths,\
                                         get_region_boundaries
from ribogadgets.settings import *
from ribogadgets.core.quantify import quantify_experiment

from multilength_test_data import *
from ribogadgets.core import create_experiment

###########################################

NPROCESS = 4

ribo_output_file = "cli_rnaseq.ribo"


class TestCLIBase(unittest.TestCase):

    def run_command(self, command):
      """
      Command must be a list.
      See examples below,
      """

      command_str    = tuple( map( str, command ) )
      process        = subprocess.Popen(command_str, 
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.PIPE)
      output, error  = process.communicate()
      output_str     = output.decode()
      error_str      = error.decode()

      return (output_str, error_str) 



    def setUp(self):
        self.tmp_files = list()

        files_and_contents = \
            [ (REF_LEN_FILE,     TRANSCRIPT_LENGTHS),
              (ANNOTATION_FILE,  TRANSCRIPT_ANNOTATION),
              (ALIGNMENT_FILE_1, READ_SET_1),
              (RNASEQ_FILE_1,    RNASEQ_DATA_1),
              (RNASEQ_FILE_2,    RNASEQ_DATA_2) ]

        for t_file, content_str in files_and_contents:
            with open(t_file, "w") as output_stream:
                print(content_str, file = output_stream)
            self.tmp_files.append(t_file)

        if os.path.isfile(ribo_output_file):
            os.remove(ribo_output_file)

        create_command = ["ribog", "create",
                          "--alignmentfile",  ALIGNMENT_FILE_1,  
                          "--name",           "merzifon",
                          "--reference",      "hg38",
                          "--lengths",        REF_LEN_FILE, 
                          "--annotation",     ANNOTATION_FILE,
                          "--metageneradius", METAGENE_RADIUS, 
                          "--leftspan",       LEFT_SPAN, 
                          "--rightspan",      RIGHT_SPAN,
                          "--lengthmin",      2, 
                          "--lengthmax",      5, 
                          "-n",               4,
                          ribo_output_file]

        output, error = self.run_command(create_command)
        if error:
            print("Error in creation of ribo:\n", error)
        self.tmp_files.append( ribo_output_file )


    def tearDown(self):
        [ os.remove(f) for f in self.tmp_files ]

#######################################################################  


class TestCLIRNASEQ(TestCLIBase):

    #@unittest.skip("temporarily skipping plot tests")
    def test_dump_annotation(self):
        command_pieces  = ["ribog", "dump", "annotation", ribo_output_file]
        output, error   = self.run_command(command_pieces)
        output_lines    = output.split("\n")
        expected_line_2 = ["GAPDH", "5", "15", "CDS", "0", "+"]
        output_line2    = output_lines[1].split()
        self.assertTrue( expected_line_2 == output_line2 )

    def test_set_rnaseq(self):
        command_pieces = ["ribog", "rnaseq", "set",
                          "--name",   "merzifon",
                          "--rnaseq", RNASEQ_FILE_1,
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)
        # Check that we don't get error messages
        self.assertEqual(output, "")
        self.assertEqual(error, "")


        # Check that --force option oworks when there is
        # existing rna-seq

        command_pieces = ["ribog", "rnaseq", "set",
                          "--name",   "merzifon",
                          "--rnaseq", RNASEQ_FILE_1,
                          "--force",
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)

    #@unittest.skip("temporarily skipping plot tests")
    def test_get_rnaseq(self):
        command_pieces = ["ribog", "rnaseq", "set",
                          "--name",   "merzifon",
                          "--rnaseq", RNASEQ_FILE_1,
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)

        command_pieces = ["ribog", "rnaseq", "get",
                          "--name", "merzifon",
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)

        output_lines          = output.split("\n")
        VEGFA_name, VEGFA_exp = output_lines[2].split()

        self.assertEqual(VEGFA_name, "VEGFA")
        self.assertTrue(np.isclose( float(VEGFA_exp), 15.46 ))


    #@unittest.skip("temporarily skipping plot tests")
    def test_delete_rnaseq(self):
        command_pieces = ["ribog",    "rnaseq", "set",
                          "--name",   "merzifon",
                          "--rnaseq", RNASEQ_FILE_1,
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)

        command_pieces = ["ribog",    "rnaseq", "delete",
                          "--name",   "merzifon",
                          "--force",
                           ribo_output_file]

        output, error   = self.run_command(command_pieces)
        print(output, error)

        ribo = h5py.File(ribo_output_file)

        self.assertTrue( RNASEQ_name not in \
                         ribo[EXPERIMENTS_name]["merzifon"].keys() )

        ribo.close()


if __name__ == '__main__':
        
    unittest.main()