#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:01:19 2018

@author: andrew
"""

import glob
import initialize
import os
from time import strftime
from time import gmtime
from astropy.io import fits
import numpy as np
import sys
import sex
from tqdm import tqdm
import psf

#median combine images using SWarp
def swarp(location, template_perc=0.33, use_config_file=True):
    location = location[:-5]
    temps = glob.glob(location+'/templates/*.fits')
    images = glob.glob(location + '/data/*_A_.fits')
    imNum = len(images)
    numImages = 0
    if use_config_file == True:
        template_perc = initialize.get_config_value('template_perc')
    if len(temps) == 1:
        temps_name = temps[0].split('/')[-1]
        numImages = int((temps_name.split('.'))[0].split('_')[-1])
    if len(temps) == 0 or numImages != len(images):
        #delete old template
        if len(temps) != 0:
            template_name = temps[0].split('/')[-1]
            os.remove(temps[0])
            try:
                os.remove("%s/psf/%s.cat" % (location, template_name[:-5]))
                os.remove("%s/psf/%s.psf" % (location, template_name[:-5]))
            except:
                pass
        #change image shapes to match each the smallest image in the set
        print("\n-> Slicing images to a common FOV...")
        shapes = []
        areas = []
        for i in tqdm(images):
            image_data = fits.getdata(i)
            shapes.append(image_data.shape)
            areas.append((image_data.shape)[0] * (image_data.shape)[1])
        min_index = areas.index(min(areas))
        #        correct_shape = max(set(shapes), key=shapes.count)
        correct_shape = shapes[min_index]
        print("\n-> FOV size (x,y): (%d, %d)" % (correct_shape[0], correct_shape[1]))
        for index in tqdm(range(len(shapes))):
            s = shapes[index]
            diff = tuple(np.subtract(s,correct_shape))
            im = images[index]
            im_hdu = fits.open(im)
            im_data = im_hdu[0].data
            im_header = im_hdu[0].header
            im_mask = (im_hdu[1].data).astype(int)
            if diff != (0,0):
                if diff[0] < 0:
                    im_data = np.concatenate((im_data, np.zeros((diff[0]*-1,s[1]))), axis=0)
                    im_mask = np.concatenate((im_mask, np.ones((diff[0]*-1,s[1]))), axis=0)
                if diff[0] > 0:
                    im_data = im_data[:-1*diff[0]]
                    im_mask = im_mask[:-1*diff[0]]
                if diff[1] < 0:
                    im_data = np.concatenate((im_data, np.zeros((im_data.shape[0],diff[1]*-1))), axis=1)
                    im_mask = np.concatenate((im_mask, np.ones((im_mask.shape[0],diff[1]*-1))), axis=1)
                if diff[1] > 0:
                    im_data = im_data[:,:diff[1]*-1]
                    im_mask = im_mask[:,:diff[1]*-1]
                hduData = fits.PrimaryHDU(im_data, header=im_header)
                hduMask = fits.ImageHDU(im_mask.astype(int))
                hduList = fits.HDUList([hduData, hduMask])
                hduList.writeto(im, overwrite=True)
            im_hdu.close()
        
        #change all masks into weight maps
        print("\n-> Converting all image masks into weight maps...")
        for i in tqdm(images):
            weight = sex.weight_map(i)
            hdu = fits.open(i, mode='update')
            data = hdu[0].data
            hdr = hdu[0].header
            try:
                if hdr['WEIGHT'] == 'N':
                    hdr.set('WEIGHT','Y')
                    hduData = fits.PrimaryHDU(data, header=hdr)
                    hduWeight = fits.ImageHDU(weight)
                    hduList = fits.HDUList([hduData, hduWeight])
                    hduList.writeto(i, overwrite=True)
            except KeyError:
                hdr.set('WEIGHT','Y')
                hduData = fits.PrimaryHDU(data, header=hdr)
                hduWeight = fits.ImageHDU(weight)
                hduList = fits.HDUList([hduData, hduWeight])
                hduList.writeto(i, overwrite=True)
            hdu.close()
        # choose only the top template_perc seeing images
        try:
            FWHMs = []
            for im in images:
                FWHMs.append(psf.fwhm(im))
            template_images = []
            while len(template_images) < round(template_perc * len(images)):
                template_images.append(images[FWHMs.index(np.min(FWHMs))])
                FWHMs.remove(np.min(FWHMs))
            images = template_images
        except FileNotFoundError:
            print("-> Error: PSF models do not exist, run PSF method first then try again.")
            sys.exit()
        initialize.create_configs(location)
        config_loc = location + '/configs/default.swarp'
        if os.path.exists(config_loc):
            template = location + "/templates/swarp_median_" + str(imNum) + ".fits"
            with open(config_loc, 'r') as config:
                data = config.readlines()
                config.close()
            data[4] = "IMAGEOUT_NAME" + "        " + template + "\n"
            data[15] = "WEIGHT_IMAGE" + "        " + "@%s/templates/weights.txt" % (location) + "\n"
            data[36] = "IMAGE_SIZE" + "        " + "%s, %s" % correct_shape[::-1] + "\n"
            with open(config_loc, 'w') as config:
                config.writelines(data)
                config.close()
            time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            og_templates = glob.glob(location + "/templates/*.fits")
            log_loc = location + "/templates/log.txt"
            tlist_loc = location + "/templates/template_inputs.txt"
            weight_list = "%s/templates/weights.txt" % (location)
            log_list = open(log_loc, "a+")
            template_list = open(tlist_loc, "w+")
            for i in images:
                template_list.write(str(i) + "[0]" + "\n")
            template_list.close()
            with open(weight_list, 'w+') as w:
                for i in images:
                    w.write("%s[1]\n" % (i))
            if images == []:
                print("-> No aligned images to combine\n")
            else:
                try:
                    print("-> Images being combined...\n")
                    os.system("swarp @%s -c %s" % (tlist_loc, config_loc))
                    log_list.write("template updated at %s UTC | method = median (SWarp) | images = %d\n" % (str(time), len(images)))
                    log_list.close()
                    if len(og_templates) > 0:
                        for o in og_templates:
                            os.system("mv %s %s/OASIS/archive/templates" % (o, initialize.loc))
                    print("\n-> Image combination successful!\n-> Template log updated\n")
                except:
                    print("-> Image combination failed\n")
                    sys.exit()
            temp_hdu = fits.open(template)
            temp_data = temp_hdu[0].data
            temp_hdr = temp_hdu[0].header
            try:
                temp_mask = fits.getdata(os.path.dirname(initialize.__file__) + '/coadd.weight.fits')
            except:
                try:
                    temp_mask = fits.getdata(os.path.dirname(initialize.__file__) + '/AIS_temp/coadd.weight.fits')
                except:
                    print('-> Error: can\'t find coadd.weight.fits\n-> Exiting...' )
                    sys.exit()
            mask_median = np.median(temp_mask)
            mask_std = np.std(temp_mask)
            threshold = mask_median - (mask_std)
            temp_mask[temp_mask < threshold] = 0
            temp_mask[temp_mask >= threshold] = 1
            masked_data = np.ma.masked_array(temp_data, mask=temp_mask)
            temp_median = np.ma.median(masked_data)
            temp_hduData = fits.PrimaryHDU(temp_data, header=temp_hdr)
            temp_hduMask = fits.ImageHDU(temp_mask)
            temp_hduList = fits.HDUList([temp_hduData, temp_hduMask])
            temp_hduList.writeto(template, overwrite=True)
            temp_hdu.close()
            temp_hdu = fits.open(template, mode='update')
            (temp_hdu[0].header).set('MEDIAN', str(temp_median))
            temp_hdu.close()
        else:
            print("\n-> No default.swarp file in target's config directory\n")
            sys.exit()
    else:
        print("-> Template already exists")
    try:
        os.remove(os.path.dirname(initialize.__file__) + '/coadd.weight.fits')
    except:
        pass