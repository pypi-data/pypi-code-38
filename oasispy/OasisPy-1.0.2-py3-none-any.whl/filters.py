#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 18:28:42 2018

@author: andrew
"""

from astropy.io import fits
import numpy as np
import glob
import copy
import sys
import psf
import datetime
import initialize

def get_sources(image, filtered=True, MR=False):
    '''
    gets all the point sources and fluxes deteced with SExtractor on a certain residual image
    the format of the outputted data is 
    first column: flux
    second: x pixel position 
    third: y pixel position
    '''
    image_name = image.split("/")[-1]
    image_name_res = image_name[:-5] + 'residual_.fits'
    length = (len(image_name)+6)*-1
    location = image[:length]
    filt_source = location + "/sources/filtered_sources.txt"
    if filtered == False:
        filt_source = location + "/sources/sources.txt"
    if MR == True and filtered == False:
        location = image.split('/')[:-1]
        location = '/'.join(location)
        location = location[:-9]
        filt_source = location + "sources/MR_sources.txt"
        image_name_res = image.split('/')[-1]
    if MR == True and filtered == True:
        location = image.split('/')[:-1]
        location = '/'.join(location)
        location = location[:-9]
        filt_source = location + "sources/MR_sources_filtered.txt"
        image_name_res = image.split('/')[-1]
    data = []
    inds = []
    with open(filt_source, 'r') as filt:
        sources = filt.readlines()
        filt.close()
    for s in sources:
        if s == (image_name_res+'\n'):
            check = True
            x = sources.index(s) + 5
            while check == True:
                x += 1
                try:
                    float(sources[x].split()[0])
                    data.append(sources[x].split())
                    inds.append(x)
                except:
                    check = False
            break
    for d in range(len(data)):
        data[d] = data[d][1:-1]
        for i in range(len(data[d])):
            data[d][i] = float(data[d][i])
    return data, inds

def get_all_sources(location, filt=True):
    images = glob.glob(location + '/data/*.fits')
    sources = []
    indices = []
    for i in images:
        d,ind = get_sources(i, filtered=filt)
        sources.append(d)
        indices.append(ind)
    return sources, indices

def source_count(location, filtered=True):
    sources, indices = get_all_sources(location, filt=filtered)
    xyCoords = []
    finalSources = []
    for s in sources:
        for i in range(len(s)):
            xyCoords.append((round(s[i][1]), round(s[i][2])))
    xyCoords_copy = copy.deepcopy(xyCoords)
    for xy in xyCoords_copy:
        xyCoords.remove(xy)
        if xy not in xyCoords and (xy[0]+1,xy[1]) not in xyCoords and (xy[0]-1,xy[1]) not in xyCoords and (xy[0],xy[1]+1) not in xyCoords and (xy[0],xy[1]-1) not in xyCoords:
            finalSources.append(xy)
    return finalSources, len(xyCoords_copy)

def get_image_names(location, filtered=False):
    source_loc = "%s/sources/sources.txt" % (location)
    if filtered == True:
        source_loc = "%s/sources/filtered_sources.txt" % (location)
    try:
        with open(source_loc, 'r') as src:
            src_lines = src.readlines()
            image_names = []
        for s in src_lines:
            if len(s.split()) == 1:
                image_names.append(s)
        return image_names
    except FileNotFoundError:
        return []

def write_total_sources(location):
    Q_min = float(initialize.get_config_value('qFloor'))
    print("\n-> Calculating detection statistics...\n")
    uniqueSources, numFilteredSources = source_count(location)
    originalSources, numSources = source_count(location, filtered=False)
    MR_sources, MR_inds = get_sources("%s/residuals/MR.fits" % (location), MR=True, filtered=False)
    MR_sources_filt, MR_inds_filt = get_sources("%s/residuals/MR.fits" % (location), MR=True, filtered=True)
    MR_sources = len(MR_sources)
    MR_sources_filt = len(MR_sources_filt)
    total_source_loc = location + '/sources/total_sources.txt'
    residuals = glob.glob(location + '/residuals/*_residual_.fits')
    bad_subtractions = 0
    date = datetime.datetime.now()
    for r in residuals:
        if (fits.getdata(r, 1) == 0).all():
            bad_subtractions += 1
    with open(total_source_loc, 'a+') as total:
        total.write('Date Run: %d/%d/%d %d:%d:%d | Number of Images Subtracted = %d\n' % (date.month, date.day, date.year, date.hour, date.minute, date.second, len(residuals)))
        total.write('Total Initial Sources: %d\n' % (numSources))
        print('\nTotal Initial Sources: %d\n' % (numSources))
        total.write('Total Filtered Sources: %d\n' % (numFilteredSources))
        print('Total Filtered Sources: %d\n' % (numFilteredSources))
        total.write('Total Unique Detections: %d\n' % (len(uniqueSources)))
        print('Total Unique Detections: %d\n' % (len(uniqueSources)))
        total.write('\nTotal Master Residual Sources: %d\n' % (MR_sources))
        print('\nTotal Master Residual Sources: %d\n' % (MR_sources))
        total.write('Total Filtered Master Residual Sources (best representation of real # of sources): %d\n' % (MR_sources_filt))
        print('Total Filtered Master Residual Sources (best representation of real # of sources): %d\n' % (MR_sources_filt))
        total.write('\nBad Subtractions (Q-Value < 0.50): %d/%d' % (bad_subtractions, len(residuals)))
        print('\nBad Subtractions (Q-Value < %.2f): %d/%d\n' % (Q_min, bad_subtractions, len(residuals)))
        total.write('\nAverage Number of Sources Per Image: %.2f\n\n\n' % (float(numFilteredSources/len(residuals))))
        print('\nAverage Number of Sources Per Image: %.2f\n\n\n' % (float(numFilteredSources/len(residuals))))
        total.close()
    print("\n-> Complete!\n")
        
def reoccuring(location, pix_dist=1.5, use_config_file=True):
    if use_config_file == True:
        pix_dist = initialize.get_config_value('pix_dist')
    sources,indices = get_all_sources(location)
    for i in range(len(sources)):
        new_sources,new_indices = get_all_sources(location)
        del_inds = []
        for j in range(len(new_sources[i])):
            inds = []
            x_low = round(new_sources[i][j][1]) - pix_dist
            x_high = round(new_sources[i][j][1]) + pix_dist
            y_low = round(new_sources[i][j][2]) - pix_dist
            y_high = round(new_sources[i][j][2]) + pix_dist
            check = 0
            for h in range(len(new_sources)):
                if h != i:
                    for k in range(len(new_sources[h])):
                        x = new_sources[h][k][1]
                        y = new_sources[h][k][2]
                        if x_low < x < x_high and y_low < y < y_high:
                            if check == 0:
                                inds.append(new_indices[i][j])
                            inds.append(new_indices[h][k])
                            check += 1
            if len(inds) >= (len(sources)/2):
                for index in inds:
                    del_inds.append(index)
        update_filtered_sources(location, del_inds)
            
def divot(image, nx=30, ny=30, MR=False):
    #this checks for 'diveted' detections usually indicative of errors in the
    #AIS psf convolution
    ind = []
    if MR == True:
        location = image.split('/')[:-1]
        location = '/'.join(location)
        location = location.replace('/residuals', '')
        image_res = image
        image_sources, indices = get_sources("%s/residuals/MR.fits" % (location), MR=True, filtered=True)
    else:
        image_res = image.replace('data','residuals')
        image_res = image_res[:-5] + 'residual_.fits'
        image_sources, indices = get_sources(image)
    image_data = fits.getdata(image_res)
    sigma = np.std(image_data)
    for s in image_sources:
        x, y = s[1], s[2]
        stamp = image_data[(round(y)-ny):(round(y)+ny+1), (round(x)-nx):(round(x)+nx+1)]
        f1 = (stamp<(sigma*-2)).sum()
        f2 = (stamp<(sigma*-4)).sum()
        f3 = (stamp<(sigma*-6)).sum()
        if f1>200 or f2>20 or f3>2:
            ind.append(indices[image_sources.index(s)])
    return ind

def update_filtered_sources(location, inds, MR=False):
    filt_source = location + "/sources/filtered_sources.txt"
    if MR == True:
        filt_source = location + "/sources/MR_sources_filtered.txt"
    upd_sources = []
    with open(filt_source, 'r') as filt:
        sources = filt.readlines()
        filt.close()
    for i in inds:
        upd_sources.append(sources[i])
    for s in upd_sources:
        sources = list(filter((s).__ne__, sources))
    with open(filt_source, 'w+') as filt:
        filt.writelines(sources)
        filt.close()    

def spread_model_filter(location, spread_model_min=-0.025, spread_model_max=0.1, MR=False, use_config_file=True):
    #filter source file by spread_model and puts the results in filtered_sources.txt
    source_loc = location + '/sources'
    source_txt_loc = source_loc + '/sources.txt'
    source_txt_filtered_loc = source_loc + '/filtered_sources.txt'
    if MR == True:
        source_txt_loc = source_loc + '/MR_sources.txt'
        source_txt_filtered_loc = source_loc + '/MR_sources_filtered.txt'
    del_lin = []
    with open(source_txt_loc, 'r') as src:
        lines = src.readlines()
        src.close()
    if use_config_file == True:
        spread_model_min = initialize.get_config_value('spread_model_min')
        spread_model_max = initialize.get_config_value('spread_model_max')
    for lin in lines:
        parse = lin.split()
        if parse != []:
            try:
                int(parse[0])
                if float(parse[-1]) < spread_model_min or float(parse[-1]) > spread_model_max:
                    del_lin.append(lin)
            except ValueError or IndexError:
                pass
    lines = [a for a in lines if a not in del_lin]
    with open(source_txt_filtered_loc, 'w+') as fil_src:
        fil_src.writelines(lines)
        fil_src.close()
        
def mask_sources_image(res_image, aperture_diam=1.5, use_config_file=True):
    if use_config_file == True:
        aperture_diam = initialize.get_config_value('aperture_diam')
    res_data = fits.getdata(res_image)
    res_mask = fits.getdata(res_image, 1)
    weight_check = False
    if fits.getval(res_image, 'WEIGHT') == 'Y':
        weight_check = True
        res_mask = (res_mask-1) * -1
    image = res_image.replace('_residual', '')
    image = image.replace('residuals', 'data')
    im_fwhm = psf.fwhm(image)
    unfiltered_sources, unfiltered_inds = get_sources(image, filtered=False)
    filtered_sources, filtered_inds = get_sources(image, filtered=True)
    for unf in unfiltered_sources:
        if unf not in filtered_sources:
            new_mask = mask_source(res_data.shape[0], res_data.shape[1], (unf[1], unf[2]), aperture_diam*im_fwhm)
            res_mask = np.logical_or(res_mask, new_mask)
    data_hdu = fits.PrimaryHDU(res_data, header=fits.getheader(res_image))
    if weight_check == True:
        mask_hdu = fits.ImageHDU((res_mask-1) * -1)
    else:
        mask_hdu = fits.ImageHDU(res_mask)
    list_hdu = fits.HDUList([data_hdu, mask_hdu])
    list_hdu.writeto(res_image, overwrite=True)
        
def mask_source(x_dim, y_dim, centroid, radius, method='disk'):
    y,x = np.ogrid[-centroid[0]:x_dim-centroid[0], -centroid[1]:y_dim-centroid[1]]
    if method == 'disk':
        mask = x*x + y*y <= radius*radius
    elif method == 'ring':
        mask = x*x + y*y == (radius*radius)
    else:
        print("-> Error: Unkown method entered\n-> Exiting...")
        sys.exit()
    return mask.astype(int)

def stamp(data, x, y, x_width, y_width):
    return data[y-y_width:y+y_width+1, x-x_width:x+x_width+1]
