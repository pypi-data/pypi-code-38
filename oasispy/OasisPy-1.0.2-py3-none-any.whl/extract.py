#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import sex
import os
import sys

def EXTRACT(path, method='both'):
    '''Extracts sources from individual residual frames located in **residuals** directory. Automatically filters out false positives and objects not of interest (see documentation for details). Uses ``SExtractor`` to create the initial sources catalogs, which are outputted to the **sources** directory.
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :param str method: Method of source extraction. Tells **OASIS** whether to extract sources from the individual residuals, the master residual, or both.
        
        * *both* (default): Runs ``SExtractor`` on both residuals and master residual.
        * *indiv*: Runs ``SExtractor`` only on residuals.
        * *MR*: Runs ``SExtractor`` only on master residual.
    
    :returns: A filtered source catalog for each image specified with the *method* parameter is created and appended to the text file *filtered_sources.txt* located in the **sources** directory. Source extraction statistics and extra info are located in *total_sources.txt*.
    
    '''
    paths = (path.replace(' ','')).split(',')
    del path
    for path in paths:
        if method == 'both':
            sex.sextractor(path)
            sex.sextractor_MR(path)
        elif method == 'indiv':
            sex.sextractor(path)
        elif method == 'MR':
            sex.sextractor_MR(path)
        else:
            print("\n-> Error: Unrecognized method. Please enter either 'both', 'indiv', or 'MR'.\n-> Exiting...")
            sys.exit()

if __name__ == '__main__':
    extract_method = input("\n-> Extract method (both/indiv/MR): ")
    path = input("-> Enter path to target's exposure time directory: ")
    if extract_method == 'indiv':
        if os.path.exists(path):
            EXTRACT(path, method='indiv')
        else:
            print("\n-> Error: Unknown path entered\n-> Please enter the path to an existing exposure time directory\n-> Exiting...\n")
            sys.exit()
    elif extract_method == 'MR':
        if os.path.exists(path):
            EXTRACT(path, method='MR')
        else:
            print("\n-> Error: Unknown path entered\n-> Please enter the path to an existing exposure time directory\n-> Exiting...\n")
            sys.exit()
    elif extract_method == 'both':
        if os.path.exists(path):
            EXTRACT(path, method='both')
        else:
            print("\n-> Error: Unknown path entered\n-> Please enter the path to an existing exposure time directory\n-> Exiting...\n")
            sys.exit()
    else:
        print("\n-> Error: Unknown method entered\n-> Please enter either 'indiv' or 'MR'\n-> Exiting...\n")
        sys.exit()