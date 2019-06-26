#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import combine_swarp
import sys
import os
import initialize

def COMBINE(path):
    '''Stacks science images into a high *S/N* template frame. Stacking method is the weighted median value of each pixel and is done by the AstrOmatic software ``SWarp`` (E. Bertin). Only the top third of science images with respect to seeing are included in the template.
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :returns: Weighted median coaddition of all science images is outputted into the **templates** directory with the name convention of *StackMethod_NumberOfImagesInDataset.fits*.
    
    '''
    paths = (path.replace(' ','')).split(',')
    del path
    for path in paths:
        location = path + '/data'
        if os.path.exists(path):
            initialize.create_configs(path)
            combine_swarp.swarp(location)
        else:
            print("\n-> Error: Unknown path entered\n-> Please enter the path to an existing exposure time directory\n-> Exiting...\n")
            sys.exit()

if __name__ == '__main__':
    path = input("\n-> Enter path to exposure time directory: ")
    COMBINE(path)
