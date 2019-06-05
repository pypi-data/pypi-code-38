#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
Math
----

Author:

* Rony Novianto (rony@novianto.tech)

Copyright © Novianto.tech
'''

import math

def spherical_to_cartesian(length, yaw, pitch):
    cos_pitch = math.cos(-pitch)
    x = length * math.cos(yaw) * cos_pitch
    y = length * math.sin(yaw) * cos_pitch
    z = length * math.sin(-pitch)
    return (x, y, z)
    
def cartesian_to_spherical(x, y, z):
    length = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    yaw = math.atan2(y, x)
    pitch = math.atan2(-z, x)
    return (length, yaw, pitch)
    
def quaternion_to_matrix(w, x, y, z):
    xx = x ** 2
    yy = y ** 2
    zz = z ** 2
    return [
        [1-2*yy-2*zz, 2*x*y-2*w*z, 2*w*y+2*x*z],
        [2*x*y+2*z*w, 1-2*xx*2*zz, 2*y*z-2*x*w],
        [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*xx-2*yy]
    ]
    
def quaternion_to_euler(h, i, j, k):
    v0 = 2.0 * (h * i + j * k)
    v1 = 1.0 - 2.0 * (i * i + j * j)
    roll = math.atan2(v0, v1)
    v = 2.0 * (h * j - k * i)
    v = min(1.0, max(-1.0, v))
    pitch = math.asin(v)
    v0 = 2.0 * (h * k + i * j)
    v1 = 1.0 - 2.0 * (j * j + k * k)
    yaw = math.atan2(v0, v1)
    return (yaw, pitch, roll)