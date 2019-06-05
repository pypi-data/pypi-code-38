#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Numpy
-----

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

import numpy
from . import math as extended_math

def from_dict(dict_object, keys, default=None):
    return numpy.array([dict_object.get(key, default) for key in keys])
    
def spherical_to_cartesian(spherical):
    return numpy.array(extended_math.spherical_to_cartesian(*spherical))
    
def cartesian_to_spherical(cartesian):
    return numpy.array(extended_math.cartesian_to_spherical(*cartesian))
    
def quaternion_to_matrix(quaternion):
    return numpy.array(extended_math.quaternion_to_matrix(*quaternion))
    
def quaternion_to_euler(quaternion):
    return numpy.array(extended_math.quaternion_to_euler(*quaternion))