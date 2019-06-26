#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:04:32 2018

@author: andrew
"""

import os
import glob
import initialize
import psf
from astropy.io import fits
import filters
import numpy as np
import sys
import MR
from tqdm import tqdm

def sextractor_MR(location, MR_method='swarp', use_config_file=True):
    '''
    runs SExtractor on master residual
    '''
    check_MR = glob.glob("%s/residuals/MR.fits" % (location))
    if check_MR == []:
        print("-> Master residual does not exist, creating it first...")
        if use_config_file == True:
            MR_method = initialize.get_config_value('MR_method')
        MR.MR(location, MR_method)
    master_res = glob.glob("%s/residuals/MR.fits" % (location))
    temp = glob.glob("%s/templates/*.fits" % (location))
    if len(master_res) == 1:
        if len(temp) == 1:
            MR = master_res[0]
            template = temp[0]
            temp_name = template.split('/')[-1]
            temp_name = temp_name[:-5]
            MR_hdu = fits.open(MR)
            MR_header = MR_hdu[0].header
            saturate = MR_header['SATURATE']
            temp_hdr = fits.getheader(template)
            pixscale = temp_hdr['PIXSCALE']
            MR_hdu.close()
            FWHM = psf.fwhm_template(template)
            config_loc = location + '/configs/default.sex'
            with open(config_loc, 'r') as config:
                data = config.readlines()
                config.close()
            data[9] = "PARAMETERS_NAME" + "        " + location + "/configs/default.param" + "\n"
            data[20] = "FILTER_NAME" + "        " + location + "/configs/default.conv" + "\n"
            with open(config_loc, 'w') as config:
                config.writelines(data)
                config.close()
            print("\n-> SExtracting master residual...")
            with open(config_loc, 'r') as config:
                data = config.readlines()
                config.close()
            data[51] = "SATUR_LEVEL" + "        " + str(saturate) + "\n"
            data[62] = "SEEING_FWHM" + "        " + str(FWHM) + "\n"
            data[106] = "PSF_NAME" + "        " + location + "/psf/" + temp_name + ".psf" + "\n"
            data[58] = "PIXEL_SCALE" + "        " + str(pixscale) + "\n"
            data[32] = "WEIGHT_IMAGE" + "        " + "%s[1]" % (MR) + "\n"
            with open(config_loc, 'w') as config:
                config.writelines(data)
                config.close()
            os.system("sextractor %s[0]> %s/sources/MR_sources.txt -c %s" % (MR, location, config_loc))
            temp_hdu_data = fits.PrimaryHDU((fits.getdata(MR))*-1, header=fits.getheader(MR))
            temp_hdu_mask = fits.ImageHDU(fits.getdata(MR, 1))
            temp_hdu_list = fits.HDUList([temp_hdu_data, temp_hdu_mask])
            temp_hdu_list.writeto("%s/residuals/MR_neg.fits" % (location))
            os.system("sextractor %s/residuals/MR_neg.fits[0]> %s/sources/MR_sources_2.txt -c %s" % (location, location, config_loc))
            append_negative_sources(MR, MR=True)
            MR_filter_sources(location)
        else:
            print("-> Error: Problem with number of template images\n-> Could not finish SExtracting master residual")
    else:
        print("-> Error: Problem with number of master residuals\n-> Could not finish SExtracting master residual")

def sextractor(location):
    '''
    runs SExtractor on all residual images
    '''
    x = 0
    sources = location + "/sources"
    residuals = location + "/residuals"
    check = os.path.exists(sources)
    check_temp = os.path.exists(sources + '/temp')
    length = len(residuals) + 1
    if check == False:
        os.system("mkdir %s" % (sources))
        os.system("mkdir %s/temp" % (sources))
    else:
        if check_temp == False:
            os.system("mkdir %s/temp" % (sources))
    images = glob.glob(residuals + "/*_residual_.fits")
    initialize.create_configs(location)
    config_loc = location + '/configs/default.sex'
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[9] = "PARAMETERS_NAME" + "        " + location + "/configs/default.param" + "\n"
    data[20] = "FILTER_NAME" + "        " + location + "/configs/default.conv" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    print("-> Converting all residual masks into weight maps...\n")
    for r in tqdm(images):
        weight = weight_map(r)
        hdu = fits.open(r, mode='update')
        data = hdu[0].data
        hdr = hdu[0].header
        try:
            if hdr['WEIGHT'] == 'N':
                hdr.set('WEIGHT','Y')
                hduData = fits.PrimaryHDU(data, header=hdr)
                hduWeight = fits.ImageHDU(weight)
                hduList = fits.HDUList([hduData, hduWeight])
                hduList.writeto(r, overwrite=True)
        except KeyError:
            hdr.set('WEIGHT','Y')
            hduData = fits.PrimaryHDU(data, header=hdr)
            hduWeight = fits.ImageHDU(weight)
            hduList = fits.HDUList([hduData, hduWeight])
            hduList.writeto(r, overwrite=True)
        hdu.close()
        try:
            if fits.getval(r, 'NORM') == 'N':
                fits.setval(r, 'NORM', value='Y')
                MR.normalize(r)
        except KeyError:
            fits.setval(r, 'NORM', value='Y')
            MR.normalize(r)
    print("\n-> SExtracting residual images...")
    for i in images:
        name = i[length:-5]
        data_name = location + '/data/' + name.replace('residual_','') + '.fits'
        FWHM = psf.fwhm(data_name)
        im_hdu = fits.open(data_name)
        im_header = im_hdu[0].header
        saturate = im_header['SATURATE']
        pixscale = im_header['PIXSCALE']
        im_hdu.close()
        with open(config_loc, 'r') as config:
            data = config.readlines()
            config.close()
        data[51] = "SATUR_LEVEL" + "        " + str(saturate) + "\n"
        data[62] = "SEEING_FWHM" + "        " + str(FWHM) + "\n"
        data[106] = "PSF_NAME" + "        " + location + "/psf/" + name[:-9] + ".psf" + "\n"
        data[58] = "PIXEL_SCALE" + "        " + str(pixscale) + "\n"
        data[32] = "WEIGHT_IMAGE" + "        " + "%s[1]" % (i) + "\n"
        with open(config_loc, 'w') as config:
            config.writelines(data)
            config.close()
        os.system("sextractor %s[0]> %s/temp/%s.txt -c %s" % (i, sources, name, config_loc))
        temp_hdu_data = fits.PrimaryHDU((fits.getdata(i))*-1, header=fits.getheader(i))
        temp_hdu_mask = fits.ImageHDU(fits.getdata(i, 1))
        temp_hdu_list = fits.HDUList([temp_hdu_data, temp_hdu_mask])
        temp_hdu_list.writeto("%s/residuals/temp.fits" % (location))
        os.system("sextractor %s/residuals/temp.fits[0]> %s/temp/%s_2.txt -c %s" % (location, sources, name, config_loc))
        append_negative_sources(i)
        os.remove("%s/residuals/temp.fits" % (location))
        x += 1
        per = float(x)/float(len(images)) * 100
        print("\t %.1f%% sextracted..." % (per))
    print("-> SExtracted %d images, catalogues placed in 'sources' directory\n" % (len(images)))
    print("-> Filtering source catalogs...\n")
    src_join(location)
    filter_sources(location)
    
def sextractor_sim(image):
    location = image.split('/')[:-2]
    location = '/'.join(location)
    sources = location + "/sources"
    check = os.path.exists(sources)
    check_temp = os.path.exists(sources + '/temp')
    if check == False:
        os.system("mkdir %s" % (sources))
        os.system("mkdir %s/temp" % (sources))
    else:
        if check_temp == False:
            os.system("mkdir %s/temp" % (sources))
    initialize.create_configs(location)
    config_loc = location + '/configs/default.sex'
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[9] = "PARAMETERS_NAME" + "        " + location + "/configs/default.param" + "\n"
    data[20] = "FILTER_NAME" + "        " + location + "/configs/default.conv" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    print("\n-> SExtracting fake image...")
    name = image.split('/')[-1]
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[106] = "PSF_NAME" + "        " + location + "/psf/" + name[:-5] + ".psf" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    os.system("sextractor %s[0]> %s/temp/%s.txt -c %s" % (image, sources, name, config_loc))
    temp_hdu_data = fits.PrimaryHDU((fits.getdata(image))*-1, header=fits.getheader(image))
    temp_hdu_mask = fits.ImageHDU(fits.getdata(image, 1))
    temp_hdu_list = fits.HDUList([temp_hdu_data, temp_hdu_mask])
    temp_hdu_list.writeto("%s/residuals/temp.fits")
    os.system("sextractor %s/residuals/temp.fits[0]> %s/temp/%s.txt -c %s" % (location, sources, name, config_loc))
    os.remove("%s/residuals/temp.fits" % (location))
    src_join(location)
    filter_sources(location)
    
def sextractor_psf(location):
    x = 0
    psf_loc = location + "/psf"
    data = location + "/data"
    templates = location + "/templates"
    check = os.path.exists(psf_loc)
    if check == False:
        os.system("mkdir %s" % (psf_loc))
    temps = glob.glob(templates + "/*.fits")
    images = glob.glob(data + "/*_A_.fits")
    for t in temps:
        images.append(t)
    cats = glob.glob(location + '/psf/*.cat')
    images_names = [(i.split('/')[-1])[:-5] for i in images]
    cats_names = [(c.split('/')[-1])[:-4] for c in cats]
    imageCats = [im for im in images_names if im not in cats_names]
    images = []
    if temps == []:
        temps.append('')
    for imcats in imageCats:
        if imcats == (temps[0].split('/')[-1])[:-5]:
            images.append(temps[0])
        else:
            images.append(location+'/data/'+imcats+'.fits')
    initialize.create_configs(location)
    config_loc = location + '/configs/psf.sex'
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[9] = "PARAMETERS_NAME" + "        " + location + "/configs/default.psfex" + "\n"
    data[19] = "FILTER_NAME" + "        " + location + "/configs/default.conv" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    print("\n-> Creating PSF catalogs...")
    if len(temps) == 1:
        for i in images:
            name = i.split('/')[-1][:-5]
            hdu = fits.open(i)
            hdr = hdu[0].header
            pixscale = hdr['PIXSCALE']
            hdu.close()
            with open(config_loc, 'r') as config:
                data = config.readlines()
                config.close()
            data[6] = "CATALOG_NAME" + "        " + psf_loc + "/" + name + ".cat" + "\n"
            data[44] = "PIXEL_SCALE" + "        " + str(pixscale) + "\n"
            with open(config_loc, 'w') as config:
                config.writelines(data)
                config.close()
            os.system("sextractor %s[0] -c %s" % (i, config_loc))
            x += 1
            per = float(x)/float(len(images)) * 100
            print("\t %.1f%% sextracted..." % (per))
        print("-> SExtracted %d images, catalogues placed in 'psf' directory\n" % (len(images)))
    else:
        print("\n-> Error: Problem with number of template images\n")
        sys.exit()
    return images

def sextractor_psf_sim(location, image):
    psf_loc = location + "/psf"
    data = location + "/data"
    check = os.path.exists(psf_loc)
    length = len(data) + 1
    if check == False:
        os.system("mkdir %s" % (psf_loc))
    initialize.create_configs(location)
    config_loc = location + '/configs/psf.sex'
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[9] = "PARAMETERS_NAME" + "        " + location + "/configs/default.psfex" + "\n"
    data[20] = "FILTER_NAME" + "        " + location + "/configs/default.conv" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    print("\n-> Creating PSF catalog of fake image...")
    name = image[length:-5]
    with open(config_loc, 'r') as config:
        data = config.readlines()
        config.close()
    data[6] = "CATALOG_NAME" + "        " + psf_loc + "/" + name + ".cat" + "\n"
    with open(config_loc, 'w') as config:
        config.writelines(data)
        config.close()
    os.system("sextractor %s[0] -c %s" % (image, config_loc))
    
def weight_map(image):
    hdu = fits.open(image)
    hduMask = hdu[1].data
    zeroMask = np.zeros(hduMask.shape)
    weightMap = (np.logical_not(np.logical_or(hduMask,zeroMask))).astype(float)
    hdu.close()
    return weightMap

def src_join(location):
    source_loc = location + '/sources'
    temp_source_loc = source_loc + '/temp'
    temp_source_files = glob.glob(temp_source_loc + '/*.txt')
    image_names = filters.get_image_names(location)
    for file in temp_source_files:
        with open(file, 'r') as fl:
            data = fl.readlines()
        data = [str(file.replace('txt','fits')[len(source_loc)+6:]) + '\n'] + data
        data.append("\n\n\n")
        with open(source_loc + '/sources.txt', 'a+') as s:
            if data[0] not in image_names:
                s.writelines(data)
        os.remove(file)
    try:
        os.rmdir(temp_source_loc)
    except:
        print("-> Error: Problem removing temp directory in '/sources'")

def filter_sources(location, mask_sources=False):
    print("\n-> Filtering out non PSF-like sources...")
    filters.spread_model_filter(location)
    print("-> Filtering out diveted detections...")
    images = glob.glob(location + '/data/*_A_.fits')
    for i in images:
        indices = filters.divot(i)
        filters.update_filtered_sources(location, indices)
    residuals = glob.glob("%s/residuals/*_residual_.fits" % (location))
    if mask_sources == True:
        for r in residuals:
            filters.mask_sources_image(r)
    
def MR_filter_sources(location):
    with open("%s/sources/MR_sources.txt" % (location), 'r') as MR_src:
        MR_lines = MR_src.readlines()
    MR_lines.insert(0, "MR.fits\n")
    with open("%s/sources/MR_sources.txt" % (location), 'w+') as MR_src:
        for line in MR_lines:
            MR_src.write(line)
    MR_loc = "%s/residuals/MR.fits" % (location)
    print("\n-> Filtering out non PSF-like sources in master residual...")
    filters.spread_model_filter(location, MR=True)
    print("-> Filtering out diveted detections in master residual...")
    indices = filters.divot(MR_loc, MR=True)
    filters.update_filtered_sources(location, indices, MR=True)
    filters.write_total_sources(location)
        
def append_negative_sources(residual, MR=False):
    location = residual.split('/')[:-2]
    location = '/'.join(location)
    name = residual.split('/')[-1]
    name = name.replace('.fits', '')
    if MR == True:
        with open("%s/sources/%s_sources_2.txt" % (location, name), 'r') as neg_sources:
            lines = neg_sources.readlines()
        with open("%s/sources/%s_sources.txt" % (location, name), 'a') as sources:
            for l in lines:
                if l[0] != '#':
                    sources.write(l)
        os.remove("%s/sources/%s_sources_2.txt" % (location, name))
    else:
        with open("%s/sources/temp/%s_2.txt" % (location, name), 'r') as neg_sources:
            lines = neg_sources.readlines()
        with open("%s/sources/temp/%s.txt" % (location, name), 'a') as sources:
            for l in lines:
                if l[0] != '#':
                    sources.write(l)
        os.remove("%s/sources/temp/%s_2.txt" % (location, name))