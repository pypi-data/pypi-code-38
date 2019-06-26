#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 18:15:27 2018

@author: andrew
"""

import pyraf.iraf
import glob
import initialize
import os
from astropy.io import fits
import numpy as np

def int_match_to_ref(location, nx=100, ny=100, use_config_file=True):
    print("\n-> Matching flux scales to reference image...")
    ref_im = glob.glob(location + '/data/*_ref_A_.fits')
    images = glob.glob(location + '/data/*_A_.fits')
    initialize.create_configs(location)
    linmatch_loc = location + '/configs/linmatch.txt'
    if os.path.exists(linmatch_loc) == False:
        os.system('touch %s' % (linmatch_loc))
    if use_config_file == True:
        nx = initialize.get_config_value('int_match_nx')
        ny = initialize.get_config_value('int_match_ny')
    for i in images:
        if i != ref_im[0]:
            try:
                fits.getval(i, 'SCALED')
            except KeyError:
                fits.setval(i, 'SCALED', value='N')
            if fits.getval(i, 'SCALED') == 'N':
                pyraf.iraf.linmatch(i+'[0]',ref_im[0]+'[0]','grid %dx %dy' % (nx,ny),linmatch_loc,output=i+'TEMP')
                temp_image = glob.glob(location + '/data/*TEMP.fits')
                temp_image_hdu = fits.open(temp_image[0])
                temp_image_data = temp_image_hdu[0].data
                image_hdu = fits.open(i, mode='update')
                image_hdr = image_hdu[0].header
                image_hdr.set('SCALED', 'Y')
                image_mask = image_hdu[1].data
                temp_image_hdu.close()
                image_hdu.close()
                image_hdr = fits.getheader(i)
                hduData = fits.PrimaryHDU(temp_image_data, header=image_hdr)
                hduMask = fits.ImageHDU(image_mask)
                hduList = fits.HDUList([hduData, hduMask])
                hduList.writeto(i, overwrite=True)
                os.system("rm %s" % (temp_image[0]))
    
def int_match_to_template(location, image, template, nx=100, ny=100):
    print("\n-> Matching flux scale to template...")
    initialize.create_configs(location)
    linmatch_loc = location + '/configs/linmatch.txt'
    if os.path.exists(linmatch_loc) == False:
        os.system('touch %s' % (linmatch_loc))
    pyraf.iraf.linmatch(image+'[0]',template+'[0]','grid %dx %dy' % (nx,ny),linmatch_loc,output=image+'TEMP')
    temp_image = glob.glob(location + '/data/*TEMP.fits')
    temp_image_hdu = fits.open(temp_image[0])
    temp_image_data = temp_image_hdu[0].data
    image_hdu = fits.open(image)
    image_hdr = image_hdu[0].header
    image_mask = image_hdu[1].data
    temp_image_masked = np.ma.MaskedArray(temp_image_data, mask=((image_mask-1)*-1))
    temp_image_median = np.ma.median(temp_image_masked)
    temp_image_hdu.close()
    image_hdu.close()
    hduData = fits.PrimaryHDU(temp_image_data, header=image_hdr)
    hduMask = fits.ImageHDU(image_mask)
    hduList = fits.HDUList([hduData, hduMask])
    hduList.writeto(image, overwrite=True)
    median_hdu = fits.open(image, mode='update')
    (median_hdu[0].header).set('MEDIAN', str(temp_image_median))
    median_hdu.close()
    os.system("rm %s" % (temp_image[0]))