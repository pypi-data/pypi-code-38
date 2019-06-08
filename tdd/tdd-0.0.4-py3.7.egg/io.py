"""
Class for io :
    - Should have methods to take data and transform to a photometry table and light curves
    - Should have methods to transform to light curves
"""
from __future__ import absolute_import, print_function, division
from future.utils import with_metaclass

__all__ = ['read_plasticc_data']
import numpy as np
import pandas as pd

def read_plasticc_data(metadata_fname, photometry_fname):
    """
    function to read the plasticc data from a single csv file
    """
    metadata = pd.read_csv(metadata_fname)
    photometry = pd.read_csv(photometry_fname)
    return metadata, photometry
