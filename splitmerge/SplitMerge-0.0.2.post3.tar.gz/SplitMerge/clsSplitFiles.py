#!/usr/bin/python

############################################
#### Written By: SATYAKI DE             ####
#### Written On: 10-Feb-2019            ####
#### Pandas, Regular Expression, gc     ####
#### needs to install in order to run   ####
#### this script.                       ####
####                                    ####
#### Objective: This script will        ####
#### initiate the splitting of large    ####
#### csv files into more managable      ####
#### small csv files.                   ####
#### based on client supplied data.     ####
############################################

import os
import pandas as p
from SplitMerge.clsLog import clsLog
import gc
import csv

class clsSplitFiles(object):
    def __init__(self, srcFileName, path, subdir):
        self.srcFileName = srcFileName
        self.path = path
        self.subdir = subdir

        # Maximum Number of rows in CSV
        # in order to avoid Memory Error
        self.max_num_rows = 30000
        self.networked_directory = 'src_file'
        self.Ind = 'Y'

    def split_files(self):
        try:
            src_dir = self.path
            subdir = self.subdir
            networked_directory = self.networked_directory

            # Initiate Logging Instances
            SplitMerge = clsLog(src_dir)

            # Setting up values
            srcFileName = self.srcFileName

            First_part, Last_part = str(srcFileName).split(".")

            num_rows = self.max_num_rows
            dest_path = self.path
            remote_src_path = src_dir + networked_directory
            Ind = self.Ind
            interval = num_rows

            # Changing work directory location to source file
            # directory at remote server
            os.chdir(remote_src_path)

            src_fil_itr_no = 1

            # Split logic here
            for df2 in p.read_csv(srcFileName, index_col=False, error_bad_lines=False, chunksize=interval):
                # Changing the target directory path
                os.chdir(dest_path)

                # Calling custom file generation method
                # to generate splitted files
                SplitMerge.logr(str(src_fil_itr_no) + '__' + First_part + '_' + '_splitted_.' + Last_part, Ind, df2, subdir)

                del [[df2]]
                gc.collect()

                src_fil_itr_no += 1

            return 0
        except Exception as e:
            x = str(e)
            print(x)

            return 1