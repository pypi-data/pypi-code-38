#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions used for correlation calculations

:Author: Gabrielle Altman gabrielle.altman@wustl.edu
:Author: Yin Hoon Chew yinhoon.chew@mssm.edu
:Date: 2019-06-19
:Copyright: 2019, Karr Lab
:License: MIT
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy import spatial
import dcor

def calculatePearsons(x, y):
    """Calculates Pearson's correlation coefficient

    Args:
        x(:obj:'pandas.DataFrame'):first set of data
        y(:obj:'pandas.DataFrame'):second set of data
        
    Returns:
        :obj:'list': list with value of Pearson's correlation coefficient and the p-value
    """
        
    xvals = x.Value.values
    yvals = y.Value.values

    coef,pval = stats.pearsonr(xvals, yvals)
        
    return [coef,pval]

def calculateSpearmans(x,y):
    """Calculates Spearman's correlation coefficient

    Args:
        x(:obj:'pandas.DataFrame'):first set of data
        y(:obj:'pandas.DataFrame'):second set of data
        
    Returns:
        :obj:'list': list with value of Spearman's correlation coefficient and the p-value
    """
    xvals = x.Value.values
    yvals = y.Value.values
        
    rho,pval = stats.spearmanr(xvals, yvals)
        
    return [rho,pval]

def calculateKendalls(x,y):
    """Calculates Kendall's tau
       
    Args:
        x(:obj:'pandas.DataFrame'):first set of data
        y(:obj:'pandas.DataFrame'):second set of data
        
    Returns:
        :obj:'list': list with value of Kendall's Tau and the p-value
    """
    xvals = x.Value.values
    yvals = y.Value.values
        
    tau,pval = stats.kendalltau(xvals, yvals)
        
    return [tau,pval]
    
def calculateDistance(x,y):
    """Calculates Distance Correlation coefficient
        
    Args:
        x(:obj:'pandas.DataFrame'):first set of data
        y(:obj:'pandas.DataFrame'):second set of data
        
    Returns:
        :obj:'float': value of distance correlation coefficient
    """
    xvals = x.Value.values
    yvals = y.Value.values
        
    corr = spatial.distance.correlation(xvals,yvals)
        
    return corr

def calculateDistanceT(x,y):
    """Calculates Kendall's tau
       
    Args:
        x(:obj:'pandas.DataFrame'):first set of data
        y(:obj:'pandas.DataFrame'):second set of data
        
    Returns:
        :obj:'list': list with value of coefficient and the p-value of T test
    """
    xvals = x.Value.values
    yvals = y.Value.values
    dval = dcor.distance_correlation(xvals,yvals)

    hypothesis = dcor.independence.distance_correlation_t_test(xvals,yvals)

    return [dval, hypothesis]




