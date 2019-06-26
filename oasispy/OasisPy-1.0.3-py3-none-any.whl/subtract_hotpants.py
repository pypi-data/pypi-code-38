#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:04:11 2018

@author: andrew
"""

import glob
import os
import psf
import numpy as np
import subtract_ais
import sys

def hotpants(location):
    '''
    subtract using hotpants
    '''
    x = 0
    images = glob.glob(location + "/data/*_A_.fits")
    template = glob.glob(location + "/templates/*.fits")
    outputs = []
    length = len(location) + 6
    psf_data = glob.glob(location + '/psf/*')
    if len(psf_data) == 3*(len(images)+1):
        if len(template) == 1:
            sig_template = psf.fwhm_template(template[0])/2.355
            for i in images:
                sig_image = psf.fwhm(i)/2.355
                if sig_template < sig_image:
                    sigma_match = np.sqrt((sig_image)**2-(sig_template)**2)
                    s1 = .5*sigma_match
                    s2 = sigma_match
                    s3 = 2*sigma_match
                    outputs.append(location + "/residuals/" + i[length:-8] + "_hotpants.fits")
                    os.system("./hotpants -inim %s -tmplim %s -outim %s -ng 3 6 %.5f 4 %.5f 2 %.5f" % (images[x], template[0], outputs[x], s1, s2, s3))
                    x += 1
                    per = float(x)/float(len(images)) * 100
                    print("-> %.1f subtracted..." % (per))
                elif sig_template >= sig_image:
                    sigma_match = np.sqrt((sig_template)**2-(sig_image)**2)
                    s1 = .5*sigma_match
                    s2 = sigma_match
                    s3 = 2*sigma_match
                    outputs.append(location + "/residuals/" + i[length:-8] + "_hotpants.fits")
                    os.system("./hotpants -inim %s -tmplim %s -outim %s -ng 3 6 %.5f 4 %.5f 2 %.5f" % (template[0], images[x], outputs[x], s1, s2, s3))
                    subtract_ais.invert_image(location + "/residuals/" + i[length:-8] + "_hotpants.fits")
                    x += 1
                    per = float(x)/float(len(images)) * 100
                    print("-> %.1f subtracted..." % (per))
        else:
            print("-> Error with number of templates")
            sys.exit()
    else:
        print("-> Error: Need PSFs before running subtraction\n-> Run psf.py first")
        sys.exit()