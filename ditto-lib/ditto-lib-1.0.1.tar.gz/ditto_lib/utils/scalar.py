#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  scalar.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements base scalar functionality
#

from ditto_lib.utils.checker import check_package
from ditto_lib.utils.logging import logger

try:
    import sklearn.preprocessing as preprocessing
except:
    preprocessing = None

def scale(method, x, y=None, weights=None):
    check_package(preprocessing, 'sklearn', 'scale')
    scale_dict = {
        'robust' : preprocessing.RobustScaler().fit_transform,
        'min_max' : preprocessing.MinMaxScaler().fit_transform,
        'standard' : preprocessing.StandardScaler().fit_transform,
        'max_abs' : preprocessing.MaxAbsScaler().fit_transform
    }
    results = scale_dict[method](x,y)
    if weights is not None:
        results = weighted(results, weights)
    return results

def weighted(data, weights):
    if len(data[0]) != len(weights):
        logger.log('error', "Length of weights != length of input data")
        logger.log('error', "Weights {} | Input data {}".format(weights, data))
        raise ValueError("Length of weights != length of input data")
    weighted_data = []
    for vector in data:
        weighted_vector = []
        for value, weight in zip(vector, weights):
            weighted_vector.append(weight * value)
        weighted_data.append(weighted_vector)
    return weighted_data