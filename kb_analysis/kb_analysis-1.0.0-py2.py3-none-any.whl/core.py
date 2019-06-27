#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code to extra data from excel file and calculate correlations to compare
transcript and protein abundance

:Author: Gabrielle Altman gabrielle.altman@wustl.edu
:Author: Yin Hoon Chew yinhoon.chew@mssm.edu
:Date: 2019-06-18
:Copyright: 2019, Karr Lab
:License: MIT
"""

import pandas as pd
import re
import numpy as np
import wc_kb
import wc_utils
import os
import pkg_resources
from scipy import stats
from scipy import spatial
import time


class ReadFile():
    """Class used to read the excel file with data
    
    Attributes:
        excel(:obj:'str'): stores string of path to excel file
    """
    
    def __init__(self, excel):
        """Initialization of class
        
        Args:
            excel(:obj:'str'): path to excel file
        """
        
        self.excel = pd.ExcelFile(excel)
    def extract(self):
        pass
    


class ProtTranAbundance(ReadFile):

    def __init__(self, excel):
        super().__init__(excel)

    def extract(self):
        """ Extracts necessary data from the excel file provided
        
        Returns:
            :obj:'list': list of the protein and transcript abundance data extracted
        """
 
        conc = pd.read_excel(self.excel, 'Concentrations')
        proteins = pd.read_excel(self.excel, 'Proteins')



        df = pd.DataFrame(columns=['SpeciesP','ValueP','SpeciesT','ValueT'])
        df['SpeciesP']= proteins.Id
        df['SpeciesT']= proteins.Transcript


        conc = conc.set_index('Species')

       
        for i in range(len(df.SpeciesP)):
            st = re.escape(df.SpeciesP[i]) + r'(\[*.\])'
            matches = conc.filter(regex = st, axis=0)
            if len(matches.Value) > 0:
                df.ValueP[i] = matches.Value[0]

            st = re.escape(df.SpeciesT[i]) + r'(\[*.\])'
            matches = conc.filter(regex = st, axis=0)
            if len(matches.Value) > 0:
                df.ValueT[i]= matches.Value[0]
    



        df = df.loc[(df['ValueP'] > 0) & (df['ValueT'] > 0)]
        
        dfP = df[['SpeciesP','ValueP']]
        dfP.columns = ['Species', 'Value']
        dfT = df[['SpeciesT','ValueT']]
        dfT.columns = ['Species', 'Value']

       

        return [dfP, dfT]

##class transcriptSize(ReadFile):
##    def __init__(self, excel):
##        super().__init__(excel)
##
##    def extractT(self):
##        #may want to change this to protein?
##        transcript = pd.read_excel(self.excel, 'Transcripts')
##        transcript = transcript[["Id","Gene","Exons"]]
##
##        transcript['length'] = 0
##
##        for i in range(len(transcript)):
##            list = transcript.Exons[i].split(',')
##            for x in list:
##                start , end = x.split(':')
##                start = int(start)
##                end = int(end)
##                transcript.length[i]= transcript.length[i] + end-start+1
##
##        return transcript
##
##
##        genes = genes[genes.Id.isin(transcript.Gene.values)]
##
