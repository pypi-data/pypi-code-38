# -*- coding: utf-8 -*-

import h5py

from .create import create_ribo
from .settings import *

########################################################
###   A P I   F O R   R I B O G A D G E T S
########################################################

# INCOMPLETE

class ribo:
    def __init__(self, file_path):
        self.handle = h5py.File(file_path)

    @property
    def experiments(self):
        return self.handle[EXPERIMENTS_name].keys()


    def __del__(self):
        self.handle.close()