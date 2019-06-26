#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 16:57:44 2018

@author: andrew
"""

from astropy.io import fits
from scipy.ndimage.filters import gaussian_filter
import numpy as np

def background_match_to_template(image, template, sigma=20):
    print("-> Matching science image background to template...")
    im_hdu = fits.open(image)
    im_data = im_hdu[0].data
    im_header = im_hdu[0].header
    im_mask = im_hdu[1].data
    temp_data = fits.getdata(template)
    temp_mask = fits.getdata(template, 1)
    master_mask = np.logical_or(im_mask, temp_mask).astype(int)
    im_data_2 = np.ma.masked_array(im_data, mask=(master_mask-1)*-1)
    im_data_2 = np.ma.MaskedArray.filled(im_data_2, fill_value=0)
    temp_data = np.ma.masked_array(temp_data, mask=(master_mask-1)*-1)
    temp_data = np.ma.MaskedArray.filled(temp_data, fill_value=0)
    residual = temp_data - im_data_2
    residual = gaussian_filter(residual, sigma)
    im_data += residual
    hduData = fits.PrimaryHDU(im_data, header=im_header)
    hduMask = fits.ImageHDU(im_mask)
    hduList = fits.HDUList([hduData, hduMask])
    hduList.writeto(image, overwrite=True)