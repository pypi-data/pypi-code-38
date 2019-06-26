#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 13:10:04 2018

@author: andrew
"""

import requests
from initialize import loc
import obtain
import os
import ref_image
import align_astroalign
import combine_swarp
from astropy.io import fits
import numpy as np
import psf
import subtract_ais
import check_saturation
import mask
from make_stars import make_gaussian_im
import extract
import shutil
import MR
from optimize import perform_optimization
import time
import filters
import glob

def TEST():
    '''Tests the installation of **OasisPy** by downloading a set of images from an online public archive, adding fake sources to one of the images, and running the dataset through the **OASIS Pipeline**.
    If the fake sources are recovered, the test is a success. The images used are 26 second exposures of exoplanet WASP-50b taken with telescopes at the Las Cumbres Observatory.
    Results of the test are compared to control results located in **OasisPy**'s source code directory.
    
    :returns: Prints either 'TEST SUCCESSFUL!' or 'Test failure: Results do not match controls'.
    
    '''
    frameNum=30 
    q_initial=1
    q_value=0.90 
    q_min=0.80
    startTime = time.time()
    #look for existing TEST folder and delete it
    og_test = loc + '/OASIS/targets/TEST'
    if os.path.exists(og_test) == True:
        shutil.rmtree(og_test)
    #get data from LCO public archive and put in target directory under 'TEST' folder
    print("\n-> Getting data from LCO...")
    object_name = 'HAT-P-37'
    response = requests.get('https://archive-api.lco.global/frames/?' +
                            'limit=%d&' % (frameNum) +
                            'RLEVEL=91&' +
                            'PROPID='+'LCOEPO2014B-007' + '&' +
                            'OBJECT='+'%s&' % (object_name) + 
                            'FILTER='+'w&' +
                            'start='+'2019-05-29'+'&'
                            'end='+'2019-05-31'+'&'
                            ).json()
    
    frames = response['results']
#    print(len(frames))
    
    #take only the first 25 frames
    frames = frames[:frameNum]
    
    #download data
    temp_loc = loc + '/OASIS/temp/'
    os.mkdir(temp_loc+'test_data')
    for frame in frames:
      with open(temp_loc + 'test_data/' + frame['filename'], 'wb') as f:
        f.write(requests.get(frame['url']).content)
        
    #funpack and move to 'TEST' folder
    obtain.process()
    obtain.movetar()
    old_data_location = obtain.rename()
    data_location = old_data_location.replace(object_name.replace(' ', '_'), 'TEST')
    os.rename("%s/OASIS/targets/%s" % (loc, object_name.replace(' ', '_')), "%s/OASIS/targets/TEST" % (loc))
    
    #align and combine images
    test_loc = data_location[:-5]
    mask.MASK(test_loc)
    check_saturation.check_saturate(test_loc + '/data')
    ref_image.ref_image(test_loc + '/data')
    align_astroalign.align2(test_loc + '/data')
    psf.PSF(test_loc)
    combine_swarp.swarp(test_loc + '/data')
    
    #get PSFs of images so fake stars with same seeing can be added
    fake_im = '02:59:10.860_A_.fits'
    print('\n-> Image %s chosen as fake image\n' % (fake_im))
    fake_residual = fake_im.replace('_A_', '_A_residual_')
    psf.PSF(test_loc)
    FWHM = psf.fwhm(test_loc + '/data/%s' % (fake_im))
    
    #add three fake stars to reference image
    print("\n-> Adding fake stars to test image...")
    hdu = fits.open(test_loc + '/data/%s' % (fake_im))
    hdu_data = hdu[0].data
    hdu_header = hdu[0].header
    hdu_mask = hdu[1].data
    
    h, w = np.shape(hdu_data)
    pos_x = [1500,200,1200]
    pos_y = [1600,1400,700]
    array = np.array([ 0.65343465,  0.50675629,  0.84946314])
    fluxes = (200000.0 * array) + 300.0
    print("\n-> Fake locations (in pixel coords):")
    print("\t X:", pos_x)
    print("\t Y:", pos_y)
    print("-> Fake fluxes (in ADUs):")
    print("\t ", fluxes)
    
    img = make_gaussian_im(h,w,fluxes=[fluxes[0],fluxes[1],fluxes[2]],x_pos=[pos_x[0],pos_x[1],pos_x[2]],
                     y_pos=[pos_y[0],pos_y[1],pos_y[2]],std=[FWHM,FWHM,FWHM])
    
    finalData = fits.PrimaryHDU(hdu_data+img, header=hdu_header)
    finalMask = fits.ImageHDU(hdu_mask)
    finalList = fits.HDUList([finalData, finalMask])
    finalList.writeto(test_loc + '/data/%s' % (fake_im), overwrite=True)
    hdu.close()
    
    #subtract images using ISIS
    subtract_ais.isis_sub(test_loc)
    perform_optimization(test_loc, qInitial=q_initial, qValue=q_value, qFloor=q_min, use_config_file=False)
    MR.MR_swarp(test_loc)
    
    #perform SExtractor on residual images
    extract.EXTRACT(test_loc)
    
    #print TEST runtime
    endTime = time.time()
    print("\n-> Total test runtime: %.3fs\n" % (endTime-startTime))
    
    residual = glob.glob(test_loc + '/residuals/%s' % (fake_residual))

    fake1_check = False
    fake2_check = False
    fake3_check = False
    
    MR_sources, inds = filters.get_sources("%s/residuals/MR.fits" % (test_loc), filtered=True, MR=True)
    for src in MR_sources:
        if 1498 < src[1] < 1502 and 1598 < src[2] < 1602:
            fake1_check = True
        elif 198 < src[1] < 202 and 1398 < src[2] < 1402:
            fake2_check = True
        elif 1198 < src[1] < 1202 and 698 < src[2] < 702:
            fake3_check = True

    if fake1_check == True and fake2_check == True and fake3_check == True:
        print("\n-> Test SUCCESSFUL!")
    else:
        print("-> Test failure: Results do not match controls")
    
    #display final residual test image
    os.system('ds9 %s -scale zscale' % (residual[0]))

if __name__ == '__main__':
    TEST()