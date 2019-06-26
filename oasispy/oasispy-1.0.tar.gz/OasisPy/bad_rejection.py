#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 18:24:04 2018

@author: andrew
"""

import glob
import sep
import numpy as np
from astropy.io import fits
import os
from initialize import loc
from initialize import get_config_value
from operator import itemgetter

def get_SNR(location, reject_sigma=1000, reject_SNR=80, use_config_file=True):
    print('-> Checking image quality...')
    #estimate average SNR for each image
    images = glob.glob(location + '/*.fits')
    SNRs = []
    bad_images = []
    if use_config_file == True:
        reject_SNR = get_config_value('reject_SNR')
        reject_sigma = get_config_value('reject_sigma')
    for i in images:
        hdu = fits.open(i)
        data = hdu[0].data
        data = data.byteswap().newbyteorder()
        bkg = np.median(data)
        try:
            try:
                objects = sep.extract(data, reject_sigma)
            except:
                try:
                    objects = sep.extract(data, reject_sigma*10)
                except:
                    objects = sep.extract(data, reject_sigma*100)
            avgSNR = float(np.average(objects['peak']/bkg))
            SNRs.append((avgSNR, i))
            if avgSNR < reject_SNR:
                bad_images.append(i)
        except:
            bad_images.append(i)
            SNRs.append((0, i))
        hdu.close()
    #move images that weren't able to be SExtracted to archives/bad_images
    print("\n-> Moving bad images to OASIS/archive/bad_images...")
    if bad_images != []:
        os.system("mkdir --parents %s/OASIS/archive/bad_images" % (loc))
    for im in bad_images:
        os.system("mv %s %s/OASIS/archive/bad_images" % (im, loc))
    print("\n-> Moved %d bad image(s) to OASIS archive" % (len(bad_images)))
    #designate image with max SNR the reference image
    ref_image = max(SNRs, key=itemgetter(0))[1]
    return ref_image