from __future__ import absolute_import, print_function

import sys
import copy
import time
import numpy
import cobra
import pandas
import bisect
import symengine
from cobra.util import solver
from optlang.symbolics import Zero
from cobra.manipulation.delete import remove_genes
from cobra.flux_analysis import flux_variability_analysis

from .riptide import *

# Create a class to house riptide output data
class riptideClass:
    def __init__(self):
        self.model = 'NULL'
        self.fluxes = 'NULL'
        self.flux_type = 'NULL'
        self.quantile_range = 'NULL'
        self.linear_coefficient_range = 'NULL'
        self.fraction_of_optimum = 'NULL'
