#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  similarity.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements base similarity functionality
#

from ditto_lib.utils.checker import check_package

try:
    from scipy import spatial
except:
    spatial = None

def similarity(method, x, y):

    def manhattan_distance(x,y):
        '''
        Return the manhattan distance between an input
        feature set when compared to another feature set
        '''
        if len(x) != len(y):
            raise ValueError("{} is not the same length as {}".format(x, y))
        else:
            return sum(abs(a-b) for a,b in zip(x,y))

    if method != 'man':
        check_package(spatial, 'scipy', 'similarity')
    similarity_dict = {
        'euc' : spatial.distance.euclidean,
        'man' : manhattan_distance,
        'jac' : spatial.distance.jaccard,
        'cos' : spatial.distance.cosine
    }
    return similarity_dict[method](x, y)