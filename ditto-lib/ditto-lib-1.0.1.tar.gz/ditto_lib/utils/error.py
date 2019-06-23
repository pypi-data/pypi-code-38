#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  error.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements base error functionality
#

from ditto_lib.utils.checker import check_package

from math import sqrt
try:
    from sklearn import metrics
except:
    metrics = None

def percent_error(prediction, target):
    '''
    Return the percent error of a predicted value compared
    to a target value 
    '''
    if (prediction == target):
        return 0
    else:
        return ( abs(prediction - target) / max(prediction, target)) * 100

def stdev(values):
    '''
    Return the standard deviation for the given
    list of values
    '''
    mean = 0
    result = 0
    for value in values:
        mean += value
    mean /= len(values)
    for value in values:
        result += ( (value - mean) **2)
    return sqrt(result / len(values))

def error(method, x, y):
    check_package(metrics, 'sklearn', 'error')
    error_dict = {
        'mse' : metrics.mean_squared_error,
        'evs' : metrics.explained_variance_score,
        'msle' : metrics.mean_squared_log_error,
        'r2' : metrics.r2_score
    }
    return error_dict[method](x, y)