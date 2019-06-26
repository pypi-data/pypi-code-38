#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import subtract_hotpants
import subtract_ais
import optimize
import psf
import glob
import sys
import MR
from initialize import get_config_value

def SUBTRACT(path, method='ois', use_config_file=True):
    '''Performs difference imaging on the science images. The template image is convolved to match the science image's PSF, then the template is subtracted from the science image.
    This process is repeated for a number of different parameter configurations until an optimal residual is found.
    The actual convolution and subtraction is done with either the ``ISIS`` package (Alard) or ``hotpants`` (Becker). See documentation for details.
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :param str method: Method of difference imaging.
    :param bool use_config_file: If ``True`` all input parameters are fetched from the local *OASIS.config* file.
    
        * *ois* (default): Optimal Image Subtraction. Christohpe Alard's ``ISIS`` package.
        * *hotpants*: Andrew Becker's ``hotpants`` program. Very similar to Alard's OIS, but differs in input parameters. May be useful to try if OIS is returning inadequate results. 
    
    :returns: All science images are differenced and the corresponding residuals are placed in the **residuals** directory with the *_residual_* suffix.
    
    '''
    paths = (path.replace(' ','')).split(',')
    del path
    for path in paths:
        if use_config_file == True:
            method = get_config_value('sub_method')
        images = glob.glob(path + '/data/*.fits')
        psf_data = glob.glob(path + '/psf/*')
        if len(psf_data) != 2*(len(images)+1):
            psf.PSF(path)
        else:
            print("\n-> PSFs already exist...")
        if method == '' or method == 'ois':
            subtract_ais.isis_sub(path)
            optimize.perform_optimization(path)
            MR.MR_swarp(path)
        elif sub_method == 'hotpants':
            subtract_hotpants.hotpants(path)
            optimize.perform_optimization(path)
            MR.MR_swarp(path)
        else:
            print("\n-> Error: Unknown method")
            sys.exit()
    
if __name__ == '__main__':
    path = input("-> Enter path to exposure time directory: ")
    sub_method = input("-> Choose subtraction method-- ois (default) or hotpants: ")
    SUBTRACT(path, method=sub_method)