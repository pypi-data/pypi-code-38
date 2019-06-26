#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 13:34:58 2018

@author: andrew
"""

import astroscrappy
import glob
from astropy.io import fits
import numpy as np
from tqdm import tqdm

def satMask(location):
    print("\n-> Building mask of saturated stars...")
    masks = []
    images = glob.glob("%s/data/*_N_.fits" % (location))
    for i in images:
        hdu = fits.open(i, mode='update')
        try:
            hdu[0].header['MASKED']
        except KeyError:
            (hdu[0].header).set('MASKED', 'N')
        if hdu[0].header['MASKED'] == 'N':
            sat = hdu[0].header['SATURATE']
            data = np.empty((hdu[0].data).shape, dtype=np.float32)
            data[:,:] = (hdu[0].data)[:,:]
            emptyMask = np.zeros(data.shape, dtype=np.uint8, order='C')
            astroscrappy.update_mask(np.asarray(data), np.asarray(emptyMask), sat, True)
            masks.append(emptyMask)
        hdu.close()
    if masks != []:
        and_comb = np.zeros(masks[0].shape)
        for x in range(masks[0].shape[0]):
            for y in range(masks[0].shape[1]):
                pixels = []
                for m in range(len(masks)):
                    pixels.append(masks[m][x,y])
                truth = int(np.all(pixels))
                and_comb[x,y] = truth
        return and_comb.astype(int)
            
def sat_test(image):
    #get saturation mask and combine with bad pixel mask
    data = fits.getdata(image)
    bpm = fits.getdata(image, 1)
    sat = fits.getval(image, 'SATURATE')
    data_sat = np.empty((data).shape, dtype=np.float32)
    data_sat[:,:] = (data)[:,:]
    emptyMask = np.zeros(data_sat.shape, dtype=np.uint8, order='C')
    astroscrappy.update_mask(np.asarray(data_sat), np.asarray(emptyMask), sat, True)
    return bpm, emptyMask, sat
    
def cosmic(image, objLim=5.0, mask_ext=2, gain_key='GAIN', readnoise_key='RDNOISE',
           sat_key='SATURATE', lin_key='MAXLIN'):
    hdu = fits.open(image, mode='update')
    hdr = hdu[0].header
    try:
        hdr['MASKED']
    except KeyError:
        hdr.set('MASKED', 'N')
    hdu.close()
    hdu = fits.open(image, mode='update')
    hdr = hdu[0].header
    if hdr['MASKED'] == 'N':
        data = hdu[0].data
        nx, ny = data.shape[0], data.shape[1]
        try:
            bpm = hdu['BPM'].data
        except KeyError:
            try:
                bpm = fits.getdata(image, mask_ext)
                bpm = bpm.astype(int)
            except Exception as esc:
                print(esc)
                bpm = np.zeros((nx,ny))
        bpm_bool = bpm.astype(bool)
        Gain = hdr[gain_key]
        readNoise = hdr[readnoise_key]
        sat = hdr[sat_key]
        if lin_key != 'NONE':
            lin = hdr[lin_key]
        else:
            lin = sat
        if lin < sat:
            sat = float(lin)
        #get saturation mask and combine with bad pixel mask
        data_sat = np.empty((hdu[0].data).shape, dtype=np.float32)
        data_sat[:,:] = (hdu[0].data)[:,:]
        emptyMask = np.zeros(data_sat.shape, dtype=np.uint8, order='C')
        astroscrappy.update_mask(np.asarray(data_sat), np.asarray(emptyMask), sat, True)
        bpm = np.logical_or(bpm, emptyMask)
        #mask cosmic rays
        cosmicMask, cosmicData = astroscrappy.detect_cosmics(data, inmask=bpm_bool, 
                                                              objlim=objLim, gain=Gain, 
                                                              readnoise=readNoise, 
                                                              satlevel=sat)
        cosmicMask = cosmicMask.astype(np.int8)
        #combine BPM and cosmic ray mask
        badPixelMask = np.empty(bpm.shape, dtype=np.uint8, order='C')
        badPixelMask[:,:] = bpm[:,:]
        masterMask = np.asarray(badPixelMask) | np.asarray(cosmicMask)
        hdr.set('MASKED', 'Y')
        hduData = fits.PrimaryHDU(cosmicData, header=hdr)
        hduMask = fits.ImageHDU(masterMask)
        hduList=  fits.HDUList([hduData, hduMask])
        hduList.writeto(image, overwrite=True)
    hdu.close()
    
def MASK(path):
    '''Masks all cosmic rays, saturated stars, and other defects in the science images. Combines the cosmic ray mask with the image's initial bad pixel mask (set to ``NULL`` if no BPM is found) to make a master mask. Uses the python package ``astroscrappy`` (see documentation for details).
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :returns: All science images are masked. The values of the ``MASKED`` keyword in their FITS headers are changed to 'Y' if masking is successful. 
    
    '''
    images = glob.glob(path + '/data/*.fits')
    print("\n-> Masking defects (cosmic rays, saturated stars, etc.)...")
    for i in tqdm(images):
        cosmic(i)
        
if __name__ == '__main__':
    path = input("-> Enter path to exposure time directory: ")
    MASK(path)
    