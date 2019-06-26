#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 18:03:23 2018

@author: andrew
"""

from astropy.io import fits
import numpy as np
import glob
import os
import initialize
import poisson_fit
import time
import math
import psf
import subtract_ais
from background import background_match_to_template

def perform_optimization(location, qValue=0.75, qFloor=0.70, qInitial=0.90, use_config_file=True):
    if use_config_file == True:
        qValue = float(initialize.get_config_value('qValue'))
        qFloor = float(initialize.get_config_value('qFloor'))
        qInitial = float(initialize.get_config_value('qInitial'))
    print("-> Searching for bad subtractions...")
    residuals = glob.glob(location + '/residuals/*_residual_.fits')
    log_loc = location + '/residuals/log.txt'
    for r in residuals:
        hdu = fits.open(r, mode='update')
        hdr = hdu[0].header
        if hdr['OPTIMIZE'] == 'N':
            startTime = time.time()
            res_name = r.split('/')[-1]
            location = r.replace('/residuals/' + res_name,'')
            image_name = res_name[:-14]
            image = location + '/data/' + image_name + '.fits'
            Q = get_qValue(image, opt=False)
            if Q <= (qInitial) or np.isnan(Q) == True:
                q_param = optimum_config(r, qValue, qFloor, bkg_match=False, sat=True)
                if q_param < qFloor or np.isnan(q_param) == True:
                    q_param_2 = optimum_config(r, qValue, qFloor, bkg_match=True, sat=True)
                    if q_param_2 < qFloor or np.isnan(q_param_2) == True:
                        log = open(log_loc, 'a+')
                        if q_param_2 > q_param:
                            q_param = q_param_2
                        endTime = time.time()
                        log.write("%s.fits | no optimal configuration found | Q=%.2f | runtime=%.2fs | residual set to zero\n" % (image_name, q_param, (endTime-startTime)))
                        log.close()
            else:
                hdr.set('OPTIMIZE', 'Y')
                log = open(log_loc, 'a+')
                log.write("%s.fits | deg_spatial=2, nstamps=18, half_mesh=5, half_stamp=10, sig2=2, sig3=4 | Q=%.2f | no optimization needed\n" % (image_name, Q))
                log.close()
        hdu.close()

def get_qValue(image, Dist='skellam', opt=True):
    return poisson_fit.fit(image, distribution=Dist, optimize=opt)

def optimum_config(image, qThresh, qFloor, bkg_match=False, sat=False, saturation=10000000):
    image_res_name = image.split("/")[-1]
    image_name = image_res_name.replace('residual_', '')
    location = image.replace(image_res_name,'')[:-11]
    temp_loc = location + '/temp'
    data_image = location + '/data/' + image_name
    print("\n-> Running parameter optimization on %s...\n" % (image_res_name))
    #check if temp folder in exposure time directory exists, if not create it
    if os.path.exists(temp_loc) == False:
        os.mkdir(temp_loc)
    #change to temp directory so the subtracted image will be outputted into here
    cwd = os.getcwd()
    os.chdir(temp_loc)
    config_loc = location + '/configs/default_config'
    template_loc = glob.glob(location + '/templates/*.fits')
    template = template_loc[0]
    #copy image, template, and config file to the temp folder
    os.system('cp %s %s' % (config_loc, temp_loc))
    os.system('cp %s %s' % (location+'/data/'+image_name, temp_loc))
    os.system('cp %s %s' % (template, temp_loc))
    #define new names of copied files
    temp_image = temp_loc + '/' + image_name
    temp_template = template.replace('templates','temp')
    #define the line number for each parameter
    deg_spatial = 17
    nstamps_x = 0
    nstamps_y = 1
    half_mesh_size = 4
    half_stamp_size = 5
    sigma_2 = 15
    sigma_3 = 16
    #define name of outputted subtraction temp image
    temp_residual = temp_loc + '/conv.fits'
    #define list of standard deviations for each parameter
    q_list_small = []
    q_list_medium = []
    q_list_large = []
    q_list_other = []
    q_list_last = []
    q_list_largest = []
    
    log_loc = location + '/residuals/log.txt'
    log = open(log_loc, 'a+')
    
    bkg_log = 'N'
    
    #if background_sub is set to True, first match background of two images
    if bkg_match == True:
        background_match_to_template(temp_image, temp_template)
        bkg_log = 'Y'
        
    #make all masked pixels above the ISIS saturation limit to hide them from the algorithm
    image_data = fits.getdata(temp_image)
    temp_data = fits.getdata(temp_template)
    res_mask = fits.getdata(image, 1)
    if np.median(res_mask) == 1:
        res_mask = (res_mask-1) * -1
    if sat == True:
        image_data += (res_mask*2*saturation)
        temp_data += (res_mask*2*saturation)
        im_hduData = fits.PrimaryHDU(image_data)
        im_hduData.writeto(temp_image, overwrite=True)
        temp_hduData = fits.PrimaryHDU(temp_data)
        temp_hduData.writeto(temp_template, overwrite=True)
    
    #the optimization process focuses on finding the best halfs sizes, and
    #the best spatial degree and nstamps that produce the overall best residual
    #start optimization with halfs sizes of (2,4)
    #check this halfs size for three spatial degree configs (0,1,2)
    #and nstamps of (3,3), (9,9), and (18,18) respectively
    startTime = time.time()
    change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                           half_stamp_size,sigma_2,sigma_3], values=[0,3,3,2,4,1.5,3])
    subtract_test(temp_loc,temp_image,temp_template)
    Q = get_qValue(data_image)
    q_list_small.append(Q)
    if qThresh <= Q <= 1:
        replace(temp_residual, image)
        endTime = time.time()
        log.write("%s | deg_spatial=0, nstamps=3, half_mesh=2, half_stamp=4, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
    #if not a good subtraction try spatial degree of 1 and nstamps of (9,9)
    else:
        change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                               half_stamp_size,sigma_2,sigma_3], values=[1,9,9,2,4,1.5,3])
        subtract_test(temp_loc,temp_image,temp_template)
        Q = get_qValue(data_image)
        q_list_small.append(Q)
        if qThresh <= Q <= 1:
            replace(temp_residual, image)
            endTime = time.time()
            log.write("%s | deg_spatial=1, nstamps=9, half_mesh=2, half_stamp=4, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
    #if not a good subtraction try spatial degree of 2 and nstamps of (18,18)
        else:
            change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                   half_stamp_size,sigma_2,sigma_3], values=[2,18,18,2,4,1.5,3])
            subtract_test(temp_loc,temp_image,temp_template)
            Q = get_qValue(data_image)
            q_list_small.append(Q)
            if qThresh <= Q <= 1:
                replace(temp_residual, image)
                endTime = time.time()
                log.write("%s | deg_spatial=2, nstamps=18, half_mesh=2, half_stamp=4, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
    #if not a good subtraction try spatial degree of 0 and nstamps of (3,3) and halfs size of (10,15) and gaussians of (3,5)
            else:
                change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                       half_stamp_size,sigma_2,sigma_3], values=[0,3,3,10,15,3,5])
                subtract_test(temp_loc,temp_image,temp_template)
                Q = get_qValue(data_image)
                q_list_largest.append(Q)
                if qThresh <= Q <= 1:
                    replace(temp_residual, image)
                    endTime = time.time()
                    log.write("%s | deg_spatial=0, nstamps=3, half_mesh=10, half_stamp=15, sig2=3, sig3=5 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                else:
    #if not a good subtraction try changing halfs size (3,5) which is the default
    #start with spatial degree of 0 and nstamps of (3,3)
                    change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                           half_stamp_size,sigma_2,sigma_3], values=[0,3,3,3,5,1.5,3])
                    subtract_test(temp_loc,temp_image,temp_template)
                    Q = get_qValue(data_image)
                    q_list_medium.append(Q)
                    if qThresh <= Q <= 1:
                        replace(temp_residual, image)
                        endTime = time.time()
                        log.write("%s | deg_spatial=0, nstamps=3, half_mesh=3, half_stamp=5, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                    else:
    #if not a good subtraction try spatial degree of 1 and nstamps of (9,9)
                        change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                               half_stamp_size,sigma_2,sigma_3], values=[1,9,9,3,5,1.5,3])
                        subtract_test(temp_loc,temp_image,temp_template)
                        Q = get_qValue(data_image)
                        q_list_medium.append(Q)
                        if qThresh <= Q <= 1:
                            replace(temp_residual, image)
                            endTime = time.time()
                            log.write("%s | deg_spatial=1, nstamps=9, half_mesh=3, half_stamp=5, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                        else:
    #if not a good subtraction try spatial degree of 2 and nstamps of (18,18)
                            change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                   half_stamp_size,sigma_2,sigma_3], values=[2,18,18,3,5,1.5,3])
                            subtract_test(temp_loc,temp_image,temp_template)
                            Q = get_qValue(data_image)
                            q_list_medium.append(Q)
                            if qThresh <= Q <= 1:    
                                replace(temp_residual, image)
                                endTime = time.time()
                                log.write("%s | deg_spatial=2, nstamps=18, half_mesh=3, half_stamp=5, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                            else:
    #if not a good subtraction try spatial degree of 1 and nstamps of (9,9) and halfs size of (10,15) and gaussians of (3,5)
                                change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                       half_stamp_size,sigma_2,sigma_3], values=[1,9,9,10,15,3,5])
                                subtract_test(temp_loc,temp_image,temp_template)
                                Q = get_qValue(data_image)
                                q_list_largest.append(Q)
                                if qThresh <= Q <= 1:
                                    replace(temp_residual, image)
                                    endTime = time.time()
                                    log.write("%s | deg_spatial=1, nstamps=9, half_mesh=10, half_stamp=15, sig2=3, sig3=5 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                else:
    #if none of the above configs worked try a halfs size of (5,10)
    #start in the same pattern with spatial degree of 0 and nstamps of (3,3)
                                    change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                           half_stamp_size,sigma_2,sigma_3], values=[0,3,3,5,10,2,4])
                                    subtract_test(temp_loc,temp_image,temp_template)
                                    Q = get_qValue(data_image)
                                    q_list_large.append(Q)
                                    if qThresh <= Q <= 1:
                                        replace(temp_residual, image)
                                        endTime = time.time()
                                        log.write("%s | deg_spatial=0, nstamps=3, half_mesh=5, half_stamp=10, sig2=2, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                    else:
    #if not a good subtraction try spatial degree of 1 and nstamps of (9,9)
                                        change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                               half_stamp_size,sigma_2,sigma_3], values=[1,9,9,5,10,2,4])
                                        subtract_test(temp_loc,temp_image,temp_template)
                                        Q = get_qValue(data_image)
                                        q_list_large.append(Q)
                                        if qThresh <= Q <= 1:
                                            replace(temp_residual, image)
                                            endTime = time.time()
                                            log.write("%s | deg_spatial=1, nstamps=9, half_mesh=5, half_stamp=10, sig2=2, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                        else:
    #if not a good subtraction try spatial degree of 2 and nstamps of (18,18)
                                            change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                           half_stamp_size,sigma_2,sigma_3], values=[2,18,18,5,10,2,4])
                                            subtract_test(temp_loc,temp_image,temp_template)
                                            Q = get_qValue(data_image)
                                            q_list_large.append(Q)
                                            if qThresh <= Q <= 1:
                                                replace(temp_residual, image)
                                                endTime = time.time()
                                                log.write("%s | deg_spatial=2, nstamps=18, half_mesh=5, half_stamp=10, sig2=3, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                            else:
    #if not a good subtraction try spatial degree of 2 and nstamps of (18,18) and halfs size of (10,15) and gaussians of (3,5)
                                                change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                           half_stamp_size,sigma_2,sigma_3], values=[2,18,18,10,15,3,5])
                                                subtract_test(temp_loc,temp_image,temp_template)
                                                Q = get_qValue(data_image)
                                                q_list_largest.append(Q)
                                                if qThresh <= Q <= 1:
                                                    replace(temp_residual, image)
                                                    endTime = time.time()
                                                    log.write("%s | deg_spatial=2, nstamps=18, half_mesh=10, half_stamp=15, sig2=3, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                else:
    #if not a good subtraction try changing halfs size (3,8)
    #start with spatial degree 0 and nstamps (3,3)
                                                    change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                               half_stamp_size,sigma_2,sigma_3], values=[0,3,3,3,8,1.5,3])
                                                    subtract_test(temp_loc,temp_image,temp_template)
                                                    Q = get_qValue(data_image)
                                                    q_list_other.append(Q)
                                                    if qThresh <= Q <= 1:
                                                        replace(temp_residual, image)
                                                        endTime = time.time()
                                                        log.write("%s | deg_spatial=0, nstamps=3, half_mesh=3, half_stamp=8, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                    else:
    #if not a good subtraction try spatial degree of 1 and nstmaps of (9,9)
                                                        change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                           half_stamp_size,sigma_2,sigma_3], values=[1,9,9,3,8,1.5,3])
                                                        subtract_test(temp_loc,temp_image,temp_template)
                                                        Q = get_qValue(data_image)
                                                        q_list_other.append(Q)
                                                        if qThresh <= Q <= 1:
                                                            replace(temp_residual, image)
                                                            endTime = time.time()
                                                            log.write("%s | deg_spatial=1, nstamps=9, half_mesh=3, half_stamp=8, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                        else:
    #if not a good subtraction try spatial degree of 2 and nstamps of (18,18)
                                                            change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                           half_stamp_size,sigma_2,sigma_3], values=[2,18,18,3,8,1.5,3])
                                                            subtract_test(temp_loc,temp_image,temp_template)
                                                            Q = get_qValue(data_image)
                                                            q_list_other.append(Q)
                                                            if qThresh <= Q <= 1:
                                                                replace(temp_residual, image)
                                                                endTime = time.time()
                                                                log.write("%s | deg_spatial=2, nstamps=18, half_mesh=3, half_stamp=8, sig2=1.5, sig3=3 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                            else:
    #if not a good subtraction try changing halfs size (4,6)
#start with spatial degree 0 and nstamps (3,3)
                                                                change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                                           half_stamp_size,sigma_2,sigma_3], values=[0,3,3,4,6,2,4])
                                                                subtract_test(temp_loc,temp_image,temp_template)
                                                                Q = get_qValue(data_image)
                                                                q_list_last.append(Q)
                                                                if qThresh <= Q <= 1:
                                                                    replace(temp_residual, image)
                                                                    endTime = time.time()
                                                                    log.write("%s | deg_spatial=0, nstamps=3, half_mesh=4, half_stamp=6, sig2=2, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                                else:
#if not a good subtraction try spatial degree of 1 and nstmaps of (9,9)
                                                                    change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                                       half_stamp_size,sigma_2,sigma_3], values=[1,9,9,4,6,2,4])
                                                                    subtract_test(temp_loc,temp_image,temp_template)
                                                                    Q = get_qValue(data_image)
                                                                    q_list_last.append(Q)
                                                                    if qThresh <= Q <= 1:
                                                                        replace(temp_residual, image)
                                                                        endTime = time.time()
                                                                        log.write("%s | deg_spatial=1, nstamps=9, half_mesh=4, half_stamp=6, sig2=2, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                                    else:
#if not a good subtraction try spatial degree of 2 and nstamps of (18,18)
                                                                        change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                                       half_stamp_size,sigma_2,sigma_3], values=[2,18,18,4,6,2,4])
                                                                        subtract_test(temp_loc,temp_image,temp_template)
                                                                        Q = get_qValue(data_image)
                                                                        q_list_last.append(Q)
                                                                        if qThresh <= Q <= 1:
                                                                            replace(temp_residual, image)
                                                                            endTime = time.time()
                                                                            log.write("%s | deg_spatial=2, nstamps=18, half_mesh=4, half_stamp=6, sig2=2, sig3=4 | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,Q,(endTime-startTime),bkg_log))
                                                                        else:
#if no parameter config worked then pick the one that gave the best residual
                                                                            for s in range(len(q_list_small)):
                                                                                if math.isnan(q_list_small[s]) == True:
                                                                                    q_list_small[s] = 0
                                                                            for m in range(len(q_list_medium)):
                                                                                if math.isnan(q_list_medium[m]) == True:
                                                                                    q_list_medium[m] = 0
                                                                            for l in range(len(q_list_large)):
                                                                                if math.isnan(q_list_large[l]) == True:
                                                                                    q_list_large[l] = 0
                                                                            for o in range(len(q_list_other)):
                                                                                if math.isnan(q_list_other[o]) == True:
                                                                                    q_list_other[o] = 0
                                                                            for z in range(len(q_list_last)):
                                                                                if math.isnan(q_list_last[z]) == True:
                                                                                    q_list_last[z] = 0
                                                                            for x in range(len(q_list_largest)):
                                                                                if math.isnan(q_list_largest[x]) == True:
                                                                                    q_list_largest[x] = 0
                                                                            max_small = np.max(q_list_small)
                                                                            max_medium = np.max(q_list_medium)
                                                                            max_large = np.max(q_list_large)
                                                                            max_other = np.max(q_list_other)
                                                                            max_last = np.max(q_list_last)
                                                                            max_largest = np.max(q_list_largest)
                                                                            total_max = np.max((max_small,max_medium,max_large,max_other,max_last, max_largest))
                                                                            if total_max == max_small:
                                                                                spatial_degree = q_list_small.index(max_small)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 2,4
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 2,4
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 2,4
                                                                                    sig_2,sig_3 = 1.5,3
                                                                            elif total_max == max_medium:
                                                                                spatial_degree = q_list_medium.index(max_medium)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 3,5
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 3,5
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 3,5
                                                                                    sig_2,sig_3 = 1.5,3
                                                                            elif total_max == max_large:
                                                                                spatial_degree = q_list_large.index(max_large)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 5,10
                                                                                    sig_2,sig_3 = 2,4
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 5,10
                                                                                    sig_2,sig_3 = 2,4
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 5,10
                                                                                    sig_2,sig_3 = 2,4
                                                                            elif total_max == max_other:
                                                                                spatial_degree = q_list_other.index(max_other)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 3,8
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 3,8
                                                                                    sig_2,sig_3 = 1.5,3
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 3,8
                                                                                    sig_2,sig_3 = 1.5,3
                                                                            elif total_max == max_last:
                                                                                spatial_degree = q_list_last.index(max_last)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 4,6
                                                                                    sig_2,sig_3 = 2,4
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 4,6
                                                                                    sig_2,sig_3 = 2,4
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 4,6
                                                                                    sig_2,sig_3 = 2,4
                                                                            elif total_max == max_largest:
                                                                                spatial_degree = q_list_largest.index(max_largest)
                                                                                if spatial_degree == 0:
                                                                                    n_x,n_y = 3,3
                                                                                    half_mesh,half_stamp = 10,15
                                                                                    sig_2,sig_3 = 3,5
                                                                                elif spatial_degree == 1:
                                                                                    n_x,n_y = 9,9
                                                                                    half_mesh,half_stamp = 10,15
                                                                                    sig_2,sig_3 = 3,5
                                                                                elif spatial_degree == 2:
                                                                                    n_x,n_y = 18,18
                                                                                    half_mesh,half_stamp = 10,15
                                                                                    sig_2,sig_3 = 3,5
                                                                            else:
                                                                                spatial_degree = 2
                                                                                n_x,n_y = 18,18
                                                                                half_mesh,half_stamp = 5,10
                                                                                sig_2,sig_3 = 2,4
                                                                                
                                                                            change_default_config(temp_loc, lines=[deg_spatial,nstamps_x,nstamps_y,half_mesh_size,
                                                                                                               half_stamp_size,sigma_2,sigma_3], 
                                                                                                  values=[spatial_degree,n_x,n_y,half_mesh,half_stamp,sig_2,sig_3])
                                                                            subtract_test(temp_loc,temp_image,temp_template)
                                                                            Q = get_qValue(data_image)
                                                                            if Q >= qFloor:
                                                                                q_original = get_qValue(data_image, opt=False)
                                                                                if Q >= q_original:
                                                                                    replace(temp_residual, image)
                                                                            else:
                                                                                replace(temp_residual, image, zeroMask=True)
                                                                            endTime = time.time()
                                                                            if qFloor <= Q <= 1:
                                                                                log.write("%s | deg_spatial=%d, nstamps=%d, half_mesh=%d, half_stamp=%d, sig2=%.1f, sig3=%d | Q=%.2f | runtime=%.2fs | background matched=%s\n" % (image_name,spatial_degree,n_x,half_mesh,half_stamp,sig_2,sig_3,Q,(endTime-startTime),bkg_log))
                                                                                log.close()
                                                                            print(max_small,max_medium,max_large,max_other,max_last,total_max)
    print("\n-> Parameters optimized- original residual overwritten")
    
    #set OPTIMIZE keyword to yes in residual FITS header
    if fits.getval(image, 'OPTIMIZE') != 'Y':
        hdu = fits.open(image, mode='update')
        hdr = hdu[0].header
        hdr.set('OPTIMIZE', 'Y')
        hdu.close()
    
    #after optimizing residual delete contents of temp then delete temp
    for file in os.listdir(temp_loc):
        file_path = os.path.join(temp_loc, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    try:
        os.rmdir(temp_loc)
    except:
        os.system("rm -r %s" % (temp_loc))
    #change directory back to original
    os.chdir(cwd)
    
    log.close()
    
    return Q

def change_default_config(location, lines=[], values=[]):
    #a function to change the parameter value of a certain line of the config file
    config_loc = location + '/default_config'
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    for i in range(len(lines)):
        old_line = data[lines[i]].split()
        old_line[1] = str(values[i])
        new_line = ' '.join(old_line) + '\n'
        data[lines[i]] = new_line
    with open(config_loc, 'w') as new_config:
        new_config.writelines(data)
        new_config.close()

def subtract_test(location, image, template, hotpants_special=False, hotpants_default=False):
    data_image = image.replace('temp', 'data')
    data_template = template.replace('temp', 'templates')
    config = location + '/default_config'
    AIS_loc = os.path.dirname(initialize.__file__) + "/AIS/package/bin/./mrj_phot"
    if hotpants_special == True:
        cwd = os.getcwd()
        os.chdir(os.path.dirname(initialize.__file__))
        sig_template = psf.fwhm_template(data_template)/2.355
        sig_image = psf.fwhm(data_image)/2.355
        if sig_template < sig_image:
            sigma_match = np.sqrt((sig_image)**2-(sig_template)**2)
            s1 = .5*sigma_match
            s2 = sigma_match
            s3 = 2*sigma_match
            output = location + "/conv.fits"
            os.system("./hotpants -inim %s[0] -tmplim %s[0] -outim %s -tmi %s[1] -imi %s[1] -ng 3 6 %.5f 4 %.5f 2 %.5f" % (image, template, output, template, image, s1, s2, s3))
        elif sig_template >= sig_image:
            sigma_match = np.sqrt((sig_template)**2-(sig_image)**2)
            s1 = .5*sigma_match
            s2 = sigma_match
            s3 = 2*sigma_match
            output = location + "/conv.fits"
            os.system("./hotpants -inim %s[0] -tmplim %s[0] -outim %s -tmi %s[1] -imi %s[1] -ng 3 6 %.5f 4 %.5f 2 %.5f" % (template, image, output, template, image, s1, s2, s3))
            subtract_ais.invert_image(output)
        os.chdir(cwd)
    elif hotpants_default == True:
        cwd = os.getcwd()
        os.chdir(os.path.dirname(initialize.__file__))
        output = location + "/conv.fits"
        os.system("./hotpants -inim %s[0] -tmplim %s[0] -outim %s -tmi %s[1] -imi %s[1]" % (image, template, output, template, image))
        os.chdir(cwd)
    else:
        os.system(AIS_loc + ' ' + template + ' ' + image + ' -c ' + config)        

def replace(new_image, old_image, zeroMask=False):
    new_data = fits.getdata(new_image)
    new_data *= -1
    old_hdu = fits.open(old_image)
    old_hdr = old_hdu[0].header
    old_mask = old_hdu[1].data
    old_hdu.close()
    if zeroMask == True:
        new_data = np.zeros(new_data.shape)
        old_mask = np.ones(new_data.shape)
    new_hduData = fits.PrimaryHDU(new_data, header=old_hdr)
    new_hduMask = fits.ImageHDU(old_mask)
    new_hduList = fits.HDUList([new_hduData, new_hduMask])
    new_hduList.writeto(old_image, overwrite=True)