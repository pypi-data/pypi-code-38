#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:58:10 2018

@author: andrew
"""

import glob
import os
from bad_rejection import get_SNR

def ref_image(location):
    '''
    rename lowest noise image to be the reference image
    '''
    ref = glob.glob(location + "/*_ref_A_.fits")
    length = len(location) + 1
    if ref == []:
        print("\n-> Selecting reference image...\n")
        ref_image = get_SNR(location)
        reference = location + "/" + ref_image[length:-8] + "_ref_A_.fits"
        os.system("mv %s %s" % (ref_image, reference))
        print("-> Designated %s as the reference image in this directory\n" % (ref_image))
    else:
        print("-> Reference image already exists in this directory\n")