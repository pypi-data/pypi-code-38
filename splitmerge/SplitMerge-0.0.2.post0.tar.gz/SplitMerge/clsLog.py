#!/usr/bin/python

############################################
#### Written By: SATYAKI DE             ####
#### Written On: 10-Feb-2019            ####
#### Pandas needs to install in order   ####
#### to run this script.                ####
####                                    ####
#### Objective: This script will        ####
#### initiate the logging/csv files     ####
#### based on client supplied data.     ####
############################################

import pandas as p
import os
import platform as pl

class clsLog(object):
    def __init__(self, path):
        self.path = path

    def logr(self, Filename, Ind, df, subdir=None):
        try:
            x = p.DataFrame()
            x = df

            sd = subdir
            os_det = pl.system()

            if os_det == "Windows":
                if sd == None:
                    fullFileName = self.path + "\\" + Filename
                else:
                    fullFileName = self.path + "\\" + sd + "\\" + Filename
            else:
                if sd == None:
                    fullFileName = self.path + "/" + Filename
                else:
                    fullFileName = self.path + "/" + sd + "/" + Filename


            if Ind == 'Y':
                x.to_csv(fullFileName, index=False)

            return 0

        except Exception as e:
            y = str(e)
            print(y)
            return 3
