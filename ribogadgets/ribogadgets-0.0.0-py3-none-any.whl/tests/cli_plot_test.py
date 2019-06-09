# -*- coding: utf-8 -*-
import unittest
from unittest import mock
from unittest.mock import patch
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

from multilength_test_data import *

###########################################

NPROCESS = 4

ribo_output_file = "cli_create.ribo"


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
              (METADATA_FILE_1,  METADATA_EXPERIMENT_STR_1),
              (RIBO_META_FILE_1, RIBO_METADATA_STR_1),
              (RNASEQ_FILE_1,    RNASEQ_DATA_1) ]

        for t_file, content_str in files_and_contents:
            with open(t_file, "w") as output_stream:
                print(content_str, file = output_stream)
            self.tmp_files.append(t_file)

        if os.path.isfile(ribo_output_file):
            os.remove(ribo_output_file)

        create_command = ["ribog", "create", 
                          "--alignmentfile",  ALIGNMENT_FILE_1,
                          "--name",          "merzifon", 
                          "--reference",     "hg38",
                          "--lengths",        REF_LEN_FILE, 
                          "--annotation",     ANNOTATION_FILE,
                          "--metageneradius", METAGENE_RADIUS, 
                          "--leftspan",       LEFT_SPAN, 
                          "--rightspan",      RIGHT_SPAN,
                          "--lengthmin",      2, 
                          "--lengthmax",      5, 
                          "--expmeta",        METADATA_FILE_1,
                          "--ribometa",       RIBO_META_FILE_1,
                          "--rnaseq",         RNASEQ_FILE_1,
                          "-n",               4, 
                          ribo_output_file]

        output, error      = self.run_command(create_command)

        #print("Output:", output)
        self.tmp_files.append( ribo_output_file )
        if output:
            print(output)
        if error:
            print(error)


    def tearDown(self):
        [ os.remove(f) for f in self.tmp_files ]

#######################################################################        


OUT_PDF = "out.pdf"

class TestCLIPlot(TestCLIBase):

    """
    def tearDown(self):
        TestCLIBase.tearDown(self)
        if os.path.exists(OUT_PDF):
            os.remove(OUT_PDF)
    """


    def test_plot_metagene_start(self):
        command_pieces = ["ribog", "plot", "metagene",
                          "--lowerlength", "2", 
                          "--upperlength", "3", 
                          "-o",            OUT_PDF,
                          "--site",        "start", 
                          ribo_output_file, "merzifon"]
        output, error = self.run_command(command_pieces)
        self.assertTrue(os.path.exists(OUT_PDF) )


    def test_plot_lengthdist(self):
        command_pieces = ["ribog", "plot", "lengthdist", 
                          "-o",        OUT_PDF, 
                          "--title",  "title_here",
                          "--region", "CDS", 
                          ribo_output_file, 
                          "merzifon"]

        output, error = self.run_command(command_pieces)

        self.assertTrue(os.path.exists(OUT_PDF) )

    def test_plot_region_counts(self):
        command_pieces = ["ribog", "plot", "regioncounts",
                          "-o",       OUT_PDF, 
                          "--title",  "title_here",
                          ribo_output_file, 
                          "merzifon"]
        output, error = self.run_command(command_pieces)
        self.assertTrue(os.path.exists(OUT_PDF) )


if __name__ == '__main__':
    unittest.main()