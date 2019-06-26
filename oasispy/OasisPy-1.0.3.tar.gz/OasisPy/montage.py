#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 18:40:54 2019

@author: andrew
"""

# Startup.  The Montage modules are pretty much self-contained
# but this script needs a few extra utilities.

import os
import sys
import shutil
import glob
from astropy.io import fits
import numpy as np

from MontagePy.main    import *
from MontagePy.archive import *

from IPython.display import Image

def MOSAIC():
    '''Interfaces with MontagePy to build a mosaic from a set of input images. All parameters are supplied through terminal prompts. See documentation for details.
    '''
    # name the mosaic project
    workdir = input("-> Name of mosaic project (ex. 'Andromeda' or 'Messier031'): ")
    
    # define location of mosaic construction
    mosaic_loc = input("-> Directory where mosaic building will take place (default = cwd): ")
    if mosaic_loc == '':
        mosaic_loc = os.getcwd()
    
    # ask how the data is being collected
    # database = FITS images from some known astronomical database
    # personal = FITS images user has already downloaded onto their machine
    data_origin = input("-> Enter method of data retrieval (database/personal): ")
    
    # get name of database
    if data_origin == 'database':
        # get region location or coordinates
        location  = input("-> Mosaic location (ex. 'M 31', '4h23m11s -12d14m32.3s'): ")
        # get name of database to download data from
        dataset = input("-> Survey/mission name and observing band (ex. SDSS g): ")
        # define size of mosaic
        size = input("-> Mosaic region size in degrees (leave blank if using personal data): ")
        if size == '':
            size = 1.0
        else:
            try:
                size = float(size)
            except:
                print("-> Error: invalid size choice\n-> Exiting...")
                sys.exit()
    elif data_origin == 'personal':
        dataset = ''
    else:
        print("-> Error: invalid input\n-> Exiting...")
        sys.exit()
    
    # We create and move into subdirectories in this notebook 
    # but we want to come back to the original startup directory 
    # whenever we restart the processing. 
    
    # move into directory where the mosaic will be built
    try:
        os.chdir(mosaic_loc)
    except FileNotFoundError:
        print('-> Mosaic location not found\n-> Creating directory now...')
        try:
            os.mkdir(mosaic_loc)
            os.chdir(mosaic_loc)
        except:
            print("-> Error: issue with creating mosaic location\n-> Exiting...")
            sys.exit()
            
    print("Mosaic location: " + mosaic_loc)
    
    # Clean out any old copy of the work tree, then remake it
    # and the set of the subdirectories we will need.
    remove_check = input("-> Remove previous mosaic data for this location if it exists? (y/n): ")
    if remove_check == 'y':
        try:
            shutil.rmtree(workdir)
        except:
            print("Can't delete work tree; probably doesn't exist yet", flush=True)
    elif remove_check == 'n':
        pass
    else:
        print("-> Error: invalid input\n-> Exiting...")
        sys.exit()
        
    # make work directory
    try:
        os.makedirs(workdir)
    except FileExistsError:
        pass
    print("Work directory: " + workdir, flush=True) 
    
    # move into work directory
    print("-> Moving into work directory...")
    os.chdir(workdir)
    
    # create necessary subfolders
    print("-> Creating subdirectories that will hold mosaic data...")
    try:
        os.makedirs("raw")
        os.makedirs("projected")
        os.makedirs("diffs")
        os.makedirs("corrected")
    except FileExistsError:
        print("-> Subdirectories already exist")
        
    # retrieve images from archive if 'database' was chosen for data_origin
    # move images into "raw" if 'personal' was chosen for data_origin
    if data_origin == 'database':
        try:
            getdata = mArchiveDownload(dataset, location, size, "raw")
            if getdata[getdata.find('count') + 8] == '0':
                print("-> Warning: No images downloaded")
        except:
            print('-> Error: issue with database information\n-> Exiting...')
            sys.exit()
    elif data_origin == 'personal':
        image_loc = input("-> Location of FITS images (if left blank you must manually move images into 'raw' directory): ")
        if image_loc != '':
            images = glob.glob("%s/*.fits" % (image_loc))
            images_gz = glob.glob("%s/*.gz" % (image_loc))
            images_fz = glob.glob("%s/*.fz" % (image_loc))
            for gz in images_gz:
                images.append(gz)
            for fz in images_fz:
                images.append(fz)
            if len(images) == 0:
                print("-> Error: Could not find any images in %s\n-> Exiting..." % (image_loc))
                sys.exit()
            for im in images:
                os.system("cp %s 'raw'" % (im))
        elif image_loc == '':
            moved = input("-> Move FITS images into 'raw' directory now\n-> (press ENTER when done)")
        else:
            print("-> Error: invalid input\n-> Exiting...")
            sys.exit()
    
    mask_ask = input("-> Read in image masks? (y/n): ")
    if mask_ask == 'y':
        mask_method = input("-> Mask type (weight map/mask): ")
        
    bkg_ask = input("-> Match image backgrounds? (y/n): ")
    
    output_image = input("-> Enter completed mosaic output image name: ")
    output_image += '.fits'
    
    # mask input images if user says so
    if mask_ask == 'n' or mask_ask == '':
        pass
    elif mask_ask == 'y':
        images = glob.glob("%s/%s/raw/*.fits" % (mosaic_loc, workdir))
        print(images)
        for i in images:
            data = fits.getdata(i)
            hdr = fits.getheader(i)
            mask = fits.getdata(i, 1)
            if mask_method == 'weight map':
                new_mask = (mask - 1) * -1
            elif mask_method == 'mask':
                new_mask = mask
            else:
                print("-> Error- Unknown input\n-> Exiting...")
                sys.exit()
            data += (new_mask*1000000000)
            data[data > 100000000] = np.nan
            hdu = fits.PrimaryHDU(data, header=hdr)
            hdu_mask = fits.ImageHDU(mask)
            hdu_list = fits.HDUList([hdu, hdu_mask])
            hdu_list.writeto(i[:-5]+'_masked.fits', overwrite=True)
            os.remove(i)
    else:
        print("-> Error- Unknown input\n-> Exiting...")
            
    
    # make table of metadata from set of FITS images in 'raw'
    print("-> Making table of metadata from selected FITS images...")
    rtn = mImgtbl("raw", "images.tbl")
    print("mImgtbl:             " + str(rtn), flush=True)
    
    # make collective FITS header to use in mosaic construction
    print("-> Making collective FITS header to use in mosaic construction...")
    rtn2 = mMakeHdr("images.tbl", "template.hdr")
    print("mMakeHdr:             " + str(rtn2), flush=True)
    
    # reproject images to the frame defined in the mMakeHdr step
    print("-> Reprojecting input images...")
    rtn3 = mProjExec("raw", "images.tbl", "template.hdr", projdir="projected")
    print("mProjExec:             " + str(rtn3), flush=True)
    
    # repeat metadata generation steps with reprojected data
    print("-> Generating metadata table again with reprojected images...")
    rtn = mImgtbl("projected", "pimages.tbl")
    print("mImgtbl (projected):             " + str(rtn), flush=True)
    
    # ask if user wants to background correct images
    if bkg_ask == 'n':
        print("-> Constructing final mosaic...")
        rtn_final = mAdd("projected", "pimages.tbl", "template.hdr", output_image)
        print("mAdd:                " + str(rtn_final), flush=True)
    elif bkg_ask == 'y' or bkg_ask == '':
        # background correct images before coaddition
        print("-> Background correcting images before coaddition...")
        # Determine the overlaps between images (for background modeling).
        rtn4 = mOverlaps("pimages.tbl", "diffs.tbl")
        print("mOverlaps:    " + str(rtn4), flush=True)
        # Generate difference images and fit them.
        rtn5 = mDiffFitExec("projected", "diffs.tbl", "template.hdr", "diffs", "fits.tbl")
        print("mDiffFitExec: " + str(rtn5), flush=True)
        # Model the background corrections.
        rtn6 = mBgModel("pimages.tbl", "fits.tbl", "corrections.tbl")
        print("mBgModel:     " + str(rtn6), flush=True)
        # Background correct the projected images.
        rtn7 = mBgExec("projected", "pimages.tbl", "corrections.tbl", "corrected")
        print("mBgExec:             " + str(rtn7), flush=True)
        # repeat metadata generation steps with reprojected and background-corrected data
        rtn = mImgtbl("corrected", "cimages.tbl")
        print("mImgtbl (corrected): " + str(rtn), flush=True)
        
        # make mosaic by coadding reprojected and background-corrected images together
        print("-> Constructing final mosaic...")
        rtn_final = mAdd("corrected", "cimages.tbl", "template.hdr", output_image)
        print("mAdd:                " + str(rtn_final), flush=True)
    else:
        print("-> Error- Unknown input\n-> Exiting...")
        sys.exit()
    
    # Make a PNG rendering of the data and display it.
    rtn_view = mViewer("-ct 1 -gray %s -2s max gaussian-log -out %s" % (output_image, output_image.replace('fits','png')), "", mode=2)
    print("mViewer: " + str(rtn_view), flush=True)
    Image(filename=output_image.replace('fits','png'))
    
if __name__ == '__main__':
    MOSAIC()