#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:28:32 2018

@author: andrew
"""

import glob
import numpy as np
from astropy.io import fits
import os
from initialize import loc
import mask
from initialize import get_config_value

#checks all fits images in a directory for saturation
def check_saturate(location, max_sat_pix=10, use_config_file=True):
    print("\n-> Checking images for saturation not found by masking...")
    Max = []
    im = []
    m = []
    y = 0
    images = glob.glob(location + "/*_N_.fits")
    if use_config_file == True:
        max_sat_pix = get_config_value('max_sat_pix')
    if images != []:
        for i in images:
            hdu = fits.open(i)
            satur = hdu[0].header['SATURATE']
            lin = hdu[0].header['MAXLIN']
            data = hdu[0].data
            try:
                MSK = hdu[1].data
            except:
                hdu.close()
                name = i.split('/')[-1]
                print('-> Error: Mask corrupted for %s, attempting to mask again...'
                      % (name))
                hdu = fits.open(i, mode='update')
                (hdu[0].header).set('MASKED', 'N')
                hdu.close()
                mask.maskImages(location[:-5])
                try:
                    hdu = fits.open(i)
                    MSK = hdu[1].data
                except:
                        hdu.close()
                        print('-> Error: Could not generate mask, moving %s to OASIS data archive' 
                              % (name))
                        os.system('mv %s %s/OASIS/archive/data' % (i, loc))
                        continue
            data = np.ma.array(data, mask=MSK)
            if satur > lin:
                lin = satur
            sat = ((data>lin)).sum()
            if sat > max_sat_pix:
                y += 1
                im.append(i)
                m.append(np.max(data))
            Max.append(np.max(data))
            sat = 0
            hdu.close()
        if y > 0:
            print("\n-> %d/%d saturated images" % (y, len(images)))
            print("\n-> average saturation level (ADU) = %d" % (np.mean(m)-lin))
            return im
        if y == 0:
            diff = lin - np.max(Max)
            print("\n-> no saturated images found")
            print("\n-> closest value to saturation = %d" % (np.max(Max)))
            print("\n-> difference between this value and saturation level = %d\n" % (diff))
            return y
    else:
        print("-> Images have already been checked for saturation")
        return 0

#move images into archives
def move_arch(images):
    archive_data_loc = loc + "/OASIS/archive/saturated_images"
    check = os.path.exists(archive_data_loc)
    if check == False:
        os.mkdir(archive_data_loc)
    for i in images:
        os.system("mv %s %s" % (i, archive_data_loc))
    print("-> Saturated images moved to OASIS archives")