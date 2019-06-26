#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import glob
import os
import shutil
import initialize
from intensity_match import int_match_to_template
from astropy.io import fits
import sys
import numpy as np

def isis_sub(location):
    x = 0
    images = glob.glob(location + "/data/*_A_.fits")
    template = glob.glob(location + "/templates/*.fits")
    residuals = glob.glob(location + "/residuals/*residual_.fits")
    images_names = [(i.split('/')[-1])[:-5] for i in images]
    res_names = [(r.split('/')[-1])[:-14] for r in residuals]
    resids = [res for res in images_names if res not in res_names]
    ims = []
    for rs in resids:
        ims.append(location+'/data/'+rs+'.fits')
    if ims != []:
        if len(template) == 1:
            ais_loc = os.path.dirname(initialize.__file__) + "/AIS/package/bin/./mrj_phot"
            initialize.create_configs(location)
            ais_config_loc = location + '/configs/default_config'
            cwd = os.getcwd()
            psf_data = glob.glob(location + '/psf/*')
            template_mask = fits.getdata(template[0], 1)
            if len(psf_data) == 2*(len(images)+1):
                try:
                    os.mkdir(cwd + "/AIS_temp")
                except FileExistsError:
                    pass
                os.chdir(cwd + "/AIS_temp")
                length = len(location) + 5
                print("\n-> Subtracting images...")
                for i in ims:
                    int_match_to_template(location, i, template[0])
                    os.system(ais_loc + " " + i + " " + template[0] + " -c " + ais_config_loc)
                    os.system("mv -f %s/AIS_temp/conv.fits %s/residuals/%sresidual_.fits" % (cwd, location, i[length:-5]))
                    hdu = fits.open(location + '/residuals/' + i[length:-5] + 'residual_.fits', mode='update')
                    hdr = hdu[0].header
                    hdr.set('OPTIMIZE', 'N')
                    hdu.close()
                    image_hdu = fits.open((i.replace('residual_', '')).replace('residuals', 'data'))
                    image_hduMask = np.logical_or(np.logical_not(image_hdu[1].data), np.logical_not(template_mask)).astype(int)
                    image_hdu.close()
                    hdu = fits.open(location + '/residuals/' + i[length:-5] + 'residual_.fits')
                    data = hdu[0].data
                    hdr = hdu[0].header
                    hdu.close()
                    hduData = fits.PrimaryHDU(data, header=hdr)
                    hduMask = fits.ImageHDU(image_hduMask)
                    hduList = fits.HDUList([hduData, hduMask])
                    hduList.writeto(location + '/residuals/' + i[length:-5] + 'residual_.fits', overwrite=True)
                    x += 1
                    per = float(x)/float(len(ims)) * 100
                    print("\t %.1f%% subtracted..." % (per))
            else:
                print("-> Error: Need PSFs before running subtraction\n-> Run psf.py first")
                print("-> If any images have been manually removed from the data directory, delete all contents of the psf directory and run OasisPy again\n")
                sys.exit()
        else:
            print("-> Subtraction failure: Template missing")
            sys.exit()
        os.chdir(cwd)
        shutil.rmtree(cwd + "/AIS_temp")
    else:
        print("-> Images have already been subtracted")