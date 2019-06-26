#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:59:13 2018

@author: andrew
"""

import os
from astropy.io import fits
import glob
from initialize import loc
import numpy as np
import astroalign
from image_registration import chi2_shift
from scipy.ndimage import shift
import intensity_match
from tqdm import tqdm

#align images to reference image using astroalign package
def align2(location, method='standard'):
    x = 1
    y = 0
    images = glob.glob(location + "/*_N_.fits")
    ref = glob.glob(location + "/*_ref_A_.fits")
    hdu2 = fits.open(ref[0])
    data2 = hdu2[0].data
    data2 = np.array(data2, dtype="float64")
    if images != []:
        if method == 'fakes':
            intensity_match.int_match_to_ref(location[:-5])
        else:
            print("\n-> Aligning images with astroalign...")
            for i in tqdm(images):
                worked = True
                hdu1 = fits.open(i)
                data1 = hdu1[0].data
                data1 = np.array(data1, dtype="float64")
                hdr1 = hdu1[0].header
                mask1 = (hdu1[1].data).astype(bool)
                data1 = np.ma.array(data1, mask=mask1)
                try:
                    try:
                        aligned = astroalign.register(data1, data2)
                        astroalign_data = (aligned.data).round(3)
                        astroalign_mask = (aligned.mask).astype(int)
                    except:
                        astroalign_data = data1
                        astroalign_mask = mask1.astype(int)
                        print("\n-> WARNING: astroalign failed, image rotation will not be accounted for\n")
                    dx,dy,edx,edy = chi2_shift(data2, astroalign_data, upsample_factor='auto')
                    alignedData = shift(astroalign_data, [-1*dy, -1*dx])
                    alignedMask = shift(astroalign_mask, [-1*dy, -1*dx], cval=1)
                except Exception as e:
                    print("\n-> Alignment failed: Moving trouble image to OASIS archive...\n")
                    print(e, '\n')
                    os.system("mkdir -p %s/OASIS/archive/failed_alignments ; mv %s %s/OASIS/archive/failed_alignments" % (loc, i, loc))
                    worked = False
                    x += 1
                    y += 1
                if worked == True:
                    aligned_name = i[:-8] + "_A_.fits"
                    #write aligned array and mask to original image location
                    hduData = fits.PrimaryHDU(alignedData, header=hdr1)
                    hduMask = fits.ImageHDU(alignedMask)
                    hduList = fits.HDUList([hduData, hduMask])
                    hduList.writeto(aligned_name, overwrite=True)
                    hdu1.close()
                    os.system("mv %s %s/OASIS/archive/data" % (i, loc))
                    x += 1
            hdu2.close()
            print("-> Sucessfuly aligned %d images \n-> Moved %d failed alignment(s) to archive" % (len(images)-y, y))
            intensity_match.int_match_to_ref(location[:-5])
    else:
        print("-> Images already aligned...")