#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import align_astroalign
from ref_image import ref_image
import check_saturation
import mask
import os
import sys
        
def ALIGN(path, align_method='standard'):
    '''Registers all science images to their reference image. If no reference image exists, one is chosen (see documentation for details).
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :param str align_method: Method of alignment. Can be either *standard* or *fakes*. Default is *standard*. The *fakes* method should be used only for simulations, as it bypasses registration and only performs photometric alignment.
    :returns: Aligns all science images are aligned to the reference image to subpixel precision. A succesful alignment changes an image's suffix from *_U_* to *_A_*.
    
    '''
    paths = (path.replace(' ','')).split(',')
    del path
    for path in paths:
        if os.path.exists(path):
            location  = path + '/data'
            mask.MASK(path)
            sat = check_saturation.check_saturate(location)
            if sat == 0:
                ref_image(location)
                align_astroalign.align2(location, method=align_method)
            else:
                check = input("-> Saturated images found, continue image alignment? (y/n): ")
                if check == 'y':
                    print("-> Moving saturated images to OASIS archives...")
                    check_saturation.move_arch(sat)
                    ref_image(location)
                    align_astroalign.align2(location, method=align_method)
                elif check =='n':
                    pass
                else:
                    print("-> Unknown input: must be y or n")
                    sys.exit()
        else:
            print("\n-> Error: Unknown path entered\n-> Please enter the path to an existing exposure time directory\n-> Exiting...\n")
            sys.exit()

if __name__ == '__main__':
    path = input("\n-> Enter path to exposure time directory: ")
    ALIGN(path)