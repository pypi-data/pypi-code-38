#!/usr/bin/python

############################################
#### Written By: SATYAKI DE             ####
#### Written On: 10-Feb-2019            ####
#### Pandas, Regular Expression, gc     ####
#### needs to install in order to run   ####
#### this script.                       ####
####                                    ####
#### Objective: This script will        ####
#### initiate the merging of smaller    ####
#### already splitted csv files         ####
#### based on client supplied data.     ####
############################################

import os
import platform as pl
import pandas as p
import gc
from SplitMerge.clsLog import clsLog
import re

class clsMergeFiles(object):

    def __init__(self, srcFilename, path):
        self.srcFilename = srcFilename
        self.subdir = 'finished'
        self.Ind = 'Y'
        self.path = path

    def merge_file(self):
        try:
            src_dir = self.path
            # Initiating Logging Instances
            df_W = p.DataFrame()
            df_M = p.DataFrame()
            f = {}

            subdir = self.subdir
            srcFilename = self.srcFilename
            Ind = self.Ind
            cnt = 0

            # Initiate Logging Instances
            SplitMerge = clsLog(src_dir)

            os_det = pl.system()

            if os_det == "Windows":
                proc_dir = "\\temp\\"
                gen_dir = "\\process\\"
            else:
                proc_dir = "/temp/"
                gen_dir = "/process/"

            # Current Directory where application presents
            path = self.path + proc_dir

            print("Path: ", path)
            print("Source File Initial Name: ", srcFilename)

            for fname in os.listdir(path):
                if fname.__contains__(srcFilename) and fname.endswith('_splitted_.csv'):
                    key = int(re.split('__', str(fname))[0])
                    f[key] = str(fname)

            for k in sorted(f):
                print(k)
                print(f[k])
                print("-"*30)

                df_W = p.read_csv(path+f[k], index_col=False)

                if cnt == 0:
                    df_M = df_W
                else:
                    d_frames = [df_M, df_W]
                    df_M = p.concat(d_frames)

                cnt += 1

                print("-"*30)
                print("Total Records in this Iteration: ", df_M.shape[0])

            FtgtFileName = fname.replace('_splitted_', '')
            first, FinalFileName = re.split("__", FtgtFileName)

            SplitMerge.logr(FinalFileName, Ind, df_M, gen_dir)

            del [[df_W], [df_M]]
            gc.collect()

            return 0
        except Exception as e:
            x = str(e)
            print(x)

            return 1