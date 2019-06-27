#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import re
import numpy as np
import wc_kb
import wc_utils
import os
import pkg_resources
from scipy import stats
from scipy import spatial
import matplotlib.pyplot as plt
import time


class openKB():

    def __init__(self, **kwargs):
        if 'file_path' in kwargs:
            self.file_path = kwargs.get('file_path')
        else:
            self.file_path = pkg_resources.resource_filename('h1_hesc',os.path.join('kb_gen','core.xlsx'))

    def runKB(self, seq_path=None):
        reader = wc_kb.io.Reader()
        if not seq_path:
            seq_path = os.path.expanduser('~/.wc/data/h1_hesc_data/genome_seq/seq.hg19.fasta')
            if not os.path.isfile(seq_path):
                mgr = wc_utils.quilt.QuiltManager(os.path.expanduser('~/.wc/data/h1_hesc_data'),'h1_hesc_data')
                mgr.download(system_path='genome_seq/seq.hg19.fasta',sym_links=True)
        kb = reader.run(self.file_path, seq_path, taxon='eukaryote')[wc_kb.KnowledgeBase][0]
        return kb

class lengths():
    def __init__(self, kb):
        self.kb=kb

    def extractLengths(self):

        cell = self.kb.cell
        protein = [i for i  in cell.species_types if type(i)==wc_kb.eukaryote_schema.ProteinSpeciesType]
        codingLength = [[(j.end-j.start+1) for j in i.coding_regions] for i in protein]
        codingLength = [sum(i) for i in codingLength]
        transcript = [i.transcript for i in protein]

        transcriptLength = [[(j.end-j.start+1) for j in i.transcript.exons] for i in protein]
        transcriptLength = [sum(i) for i in transcriptLength]

        genes = [i.gene for i in transcript]
        geneLength = [(i.end-i.start+1) for i in genes]

        
        codingLength = pd.DataFrame(np.array(codingLength).reshape(len(codingLength),1), columns =["Value"])
        transcriptLength = pd.DataFrame(np.array(transcriptLength).reshape(len(transcriptLength),1), columns =["Value"])
        geneLength = pd.DataFrame(np.array(geneLength).reshape(len(geneLength),1), columns =["Value"])

        return [codingLength, transcriptLength, geneLength]

def graph(x,y):
    plt.scatter(x,y)
    plt.show()
    


        
