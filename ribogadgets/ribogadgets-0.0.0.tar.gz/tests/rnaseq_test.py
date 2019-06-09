# -*- coding: utf-8 -*-
import unittest

import os
from io import StringIO, BytesIO

import numpy as np
import pandas as pd
import h5py


from ribogadgets import create
from ribogadgets.core.coverage import find_coverage
from ribogadgets.core.get_gadgets import get_reference_names,\
                                         get_reference_lengths,\
                                         get_region_boundaries
from ribogadgets.settings import *
from ribogadgets.dump import *
from ribogadgets.rnaseq import *

from ribogadgets.merge import merge_ribos

from multilength_test_data import *
from ribogadgets.core import create_experiment

###########################################

NPROCESS = 4

class TestCreate(unittest.TestCase):

    def setUp(self):
        self.ref_len_file    = StringIO(TRANSCRIPT_LENGTHS)
        self.annotation_file = StringIO(TRANSCRIPT_ANNOTATION)
        self.alignment_file  = StringIO(READ_SET_1)

        self.handle = h5py.File(BytesIO())

        create.create_ribo(     self.handle, "merzifon", 
                                alignment_file  = self.alignment_file,
                                reference_name  = "appris_human_v2",
                                length_min      = 2,
                                length_max      = 5,
                                metagene_radius = METAGENE_RADIUS,
                                left_span       = LEFT_SPAN, 
                                right_span      = RIGHT_SPAN,
                                lengths_file    = self.ref_len_file,
                                store_coverage  = True,
                                annotation_file = self.annotation_file)

    def tearDown(self):
        self.handle.close()

    def initial_rnaseq(self):
        rnaseq_lines = RNASEQ_DATA_1.split("\n")
        rnaseq_expression  = tuple( map(lambda x: x.split()[1] , rnaseq_lines) )
        rnaseq_expression  = np.array(rnaseq_expression, dtype = RNASEQ_DT)
        rnaseq_transcripts = tuple( map(lambda x: x.split()[0] , rnaseq_lines) )
        rnaseq_df = pd.DataFrame( rnaseq_expression, index = rnaseq_transcripts )

        set_rnaseq(self.handle, "merzifon", rnaseq_df)

    ### T E S T   R N A S E Q  ################################

    def test_set_rnaseq(self):
        self.initial_rnaseq()

        stored_rnaseq =  self.handle[EXPERIMENTS_name]\
                            ["merzifon"][RNASEQ_name][RNASEQ_name][...]
        self.assertTrue( all(np.isclose( [2.89, 15.46, 8], stored_rnaseq ) ) )

        self.assertTrue(not all(np.isclose( [2.89, 15.46, 8.25], stored_rnaseq ) ) )

        expression_2    = np.array([0.5, 983.972] , dtype = RNASEQ_DT)
        t_list_2        = ["MYC", "GAPDH"]
        rnaseq_df_2     = pd.DataFrame( expression_2, index = t_list_2 )

        set_rnaseq(self.handle, "merzifon", rnaseq_df_2)
        stored_rnaseq_2 =  self.handle[EXPERIMENTS_name]\
                            ["merzifon"][RNASEQ_name][RNASEQ_name][...]

        # Note that the order changes and VEGFA has 0
        self.assertTrue( all(np.isclose( [983.972, 0, 0.5], stored_rnaseq_2 ) ) )


    def test_get_rnaseq(self):
        self.initial_rnaseq()

        read_rnaseq = get_rnaseq(self.handle, "merzifon")

        read_transcripts = tuple(read_rnaseq.index)
        read_expression  = read_rnaseq["merzifon"]

        self.assertEqual( read_transcripts[0], "GAPDH" )
        self.assertEqual( read_transcripts[2], "MYC" )

        self.assertTrue( all(np.isclose( [2.89, 15.46, 8], read_expression ) ) )


    def test_delete_rnaseq(self):
        self.initial_rnaseq()

        self.assertTrue(RNASEQ_name in \
                         tuple(self.handle[EXPERIMENTS_name]["merzifon"].keys() ))

        delete_rnaseq(self.handle, "merzifon")

        self.assertTrue(RNASEQ_name not in \
                         tuple(self.handle[EXPERIMENTS_name]["merzifon"].keys() ))






class TestRNASEQFROMMERGED(unittest.TestCase):

    def setUp(self):
        self.tmp_files = list()


        self.ref_len_file       = StringIO(TRANSCRIPT_LENGTHS)
        self.annotation_file    = StringIO(TRANSCRIPT_ANNOTATION)
        self.alignment_file_1   = StringIO(READ_SET_1)
        self.alignment_file_2   = StringIO(READ_SET_2)

        self.handle   = h5py.File(BytesIO() )
        self.handle_2 = h5py.File(BytesIO() )

        create.create_ribo(
                ribo            = self.handle, 
                experiment_name = "merzifon", 
                alignment_file  = self.alignment_file_1,
                reference_name  = "hg38",
                lengths_file    = self.ref_len_file, 
                annotation_file = self.annotation_file,
                metagene_radius = METAGENE_RADIUS, 
                left_span       = LEFT_SPAN, 
                right_span      = RIGHT_SPAN,
                length_min      = 2,
                length_max      = 5,  
                nprocess        = NPROCESS,
                tmp_file_prefix = "")
        self.ref_len_file.seek(0)
        self.annotation_file.seek(0)
        self.alignment_file_1 = StringIO(READ_SET_1)

        
        create.create_ribo(
                ribo            = self.handle_2, 
                experiment_name = "ankara", 
                alignment_file  = self.alignment_file_2,
                reference_name  = "hg38",
                lengths_file    = self.ref_len_file, 
                annotation_file = self.annotation_file,
                metagene_radius = METAGENE_RADIUS, 
                left_span       = LEFT_SPAN, 
                right_span      = RIGHT_SPAN,
                length_min      = 2,
                length_max      = 5,
                nprocess        = NPROCESS,
                tmp_file_prefix = "")
        self.ref_len_file.seek(0)
        self.annotation_file.seek(0)
        self.alignment_file_2 = StringIO(READ_SET_2)

        self.merged_ribo_without_rnaseq = h5py.File(BytesIO(), "w")
        merge_ribos( self.merged_ribo_without_rnaseq, 
                     [self.handle , self.handle_2] )


        rnaseq_lines = RNASEQ_DATA_1.split("\n")
        rnaseq_expression  = tuple( map(lambda x: x.split()[1] , rnaseq_lines) )
        rnaseq_expression  = np.array(rnaseq_expression, dtype = RNASEQ_DT)
        rnaseq_transcripts = tuple( map(lambda x: x.split()[0] , rnaseq_lines) )
        rnaseq_df = pd.DataFrame( rnaseq_expression, index = rnaseq_transcripts )

        set_rnaseq(self.handle, 
                   name      = "merzifon", 
                   rnaseq_df = rnaseq_df)

        rnaseq_lines = RNASEQ_DATA_2.split("\n")
        rnaseq_expression  = tuple( map(lambda x: x.split()[1] , rnaseq_lines) )
        rnaseq_expression  = np.array(rnaseq_expression, dtype = RNASEQ_DT)
        rnaseq_transcripts = tuple( map(lambda x: x.split()[0] , rnaseq_lines) )
        rnaseq_df = pd.DataFrame( rnaseq_expression, index = rnaseq_transcripts )

        set_rnaseq(self.handle_2, 
                   name      = "ankara", 
                   rnaseq_df = rnaseq_df)

        self.merged_ribo = h5py.File(BytesIO(), "w")
        merge_ribos( self.merged_ribo, [self.handle , self.handle_2] )

    def test_from_merged(self):

        all_rnaseq = get_rnaseq(self.merged_ribo)

        self.assertTrue( all(np.isclose(all_rnaseq["merzifon"] , [2.89, 15.46, 8]) ) )
        self.assertTrue( all(np.isclose(all_rnaseq["ankara"] , [6.42, 1.37, 0.06]) ) )

    def test_from_no_rnaseq(self):

        all_no_rnaseq = get_rnaseq(self.merged_ribo_without_rnaseq)

        self.assertTrue( not all_no_rnaseq)


if __name__ == '__main__':
        
    unittest.main()