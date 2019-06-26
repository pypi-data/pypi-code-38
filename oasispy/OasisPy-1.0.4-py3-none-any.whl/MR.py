#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 19:24:55 2019

@author: andrew
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 11:33:23 2019

@author: andrew
"""

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from astropy.io import fits
import glob
import sex
import os
import initialize
import sys
from tqdm import tqdm

def MR_other(location, mode='sos_abs', sigma_thresh=4, gauss_sigma=3, gauss_filter=False):
    print("\n-> Constructing master residual...")
    residual_list = []
    masks = []
    median_list = []
    means = []
    residuals = glob.glob("%s/residuals/*_residual_.fits" % (location))
    mResidual = glob.glob("%s/residuals/*MR.fits" % (location))
    #fill all masked values with zero
    zeros_mask(location)
    if len(mResidual) == 0:
        if len(residuals) != 0:
            if fits.getval(residuals[0], 'WEIGHT') == 'Y':
                mask_value = 1
            else:
                mask_value = 0
            for r in residuals:
                hdu = fits.open(r)
                residual_list.append(hdu[0].data)
                median_list.append(np.median(hdu[0].data))
                masks.append(hdu[1].data)
                hdu.close()
            master_residual = np.zeros(residual_list[0].shape)
            master_mask = np.zeros(residual_list[0].shape)
            for i in tqdm(range(residual_list[0].shape[0])):
                for j in range(residual_list[0].shape[1]):
                    pixels = []
                    for res in range(len(residual_list)):
                        if masks[res][i,j] == mask_value:
                            pixels.append(residual_list[res][i,j])
                    if pixels != []:
                        if mode == 'sigma_clip':
                            MR_mask_pixel = mask_value
                            median = np.median(pixels)
                            stdev = np.std(pixels)
                            if np.max(pixels) >= (median + sigma_thresh*stdev):
                                MR_pixel = np.max(pixels)
                            elif np.min(pixels) <= (median - sigma_thresh*stdev):
                                MR_pixel = np.min(pixels) * -1
                            else:
                                MR_pixel = np.median(pixels)
                        elif mode == 'sos_abs':
                            pixels = np.array(pixels)
                            MR_pixel = np.sum(pixels*abs(pixels))
                            MR_mask_pixel = mask_value
                        elif mode == 'sos':
                            pixels = np.array(pixels)
                            MR_pixel = np.sum(pixels*pixels)
                            MR_mask_pixel = mask_value
                        else:
                            print("\n-> Error: Unrecognized mode\n-> Please use either 'sos', 'sos_abs', or 'sigma_clip'\n-> Exiting...")
                            sys.exit()
                    else:
                        MR_pixel = np.median(median_list)
                        MR_mask_pixel = (mask_value-1)*-1
                    master_residual[i,j] = MR_pixel
                    master_mask[i,j] = MR_mask_pixel                    
            template = glob.glob("%s/templates/*.fits" % (location))
            if len(template) == 1:
                temp_hdu = fits.open(template[0])
                temp_header = temp_hdu[0].header
                temp_hdu.close()
                if gauss_filter == True:
                    master_residual = gaussian_filter(master_residual, gauss_sigma)
                hduData = fits.PrimaryHDU(master_residual, header=temp_header)
                hduMask = fits.ImageHDU(master_mask)
                hduList = fits.HDUList([hduData, hduMask])
                hduList.writeto("%s/residuals/MR.fits" % (location), overwrite=True)
            else:
                print("-> Error: Problem with number of template images, couldn't complete master residual construction")
    elif len(mResidual) == 1:
        print("-> Master residual already exists...")
    else:
        print("-> Error: Problem with number of master residuals")
    return means
        
def MR_swarp(location):
    print("\n-> Constructing master residual...\n")
    residuals = glob.glob("%s/residuals/*residual_.fits" % (location))
    MR_loc = "%s/residuals/MR.fits" % (location)
    if residuals != []:
        if os.path.exists(MR_loc) == False:
            #first change all masks into weight maps
            print("-> Converting all residual masks into weight maps...\n")
            for r in tqdm(residuals):
                weight = sex.weight_map(r)
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
                        normalize(r)
                except KeyError:
                    fits.setval(r, 'NORM', value='Y')
                    normalize(r)
            #fill all masked values with zero
            zeros_mask(location)
            #make lists of residuals and their weight maps
            residual_list = "%s/residuals/inputs.txt" % (location)
            weight_list = "%s/templates/weights.txt" % (location)
            with open(residual_list, 'w+') as i:
                for r in residuals:
                    i.write("%s[0]\n" % (r))
            with open(weight_list, 'w+') as w:
                for r in residuals:
                    w.write("%s[1]\n" % (r))
            #customize swarp config file for MR
            initialize.create_configs(location)
            test_data = fits.getdata(residuals[0])
            correct_shape = test_data.shape
            config_loc=  "%s/configs/default.swarp.MR" % (location)
            with open(config_loc, 'r') as conf:
                lines = conf.readlines()
            lines[4] = "IMAGEOUT_NAME" + "        " + "%s/residuals/MR.fits" % (location) + "\n"
            lines[5] = "WEIGHTOUT_NAME" + "        " + "%s/residuals/MR_swarp_weight.fits" % (location) + "\n"
            lines[15] = "WEIGHT_IMAGE" + "        " + "@%s/templates/weights.txt" % (location) + "\n"
            lines[38] = "IMAGE_SIZE" + "        " + "%s, %s" % correct_shape[::-1] + "\n"
            with open(config_loc, 'w') as conf:
                conf.writelines(lines)
            #perform image combination
            try:
                os.system("swarp @%s/residuals/inputs.txt -c %s" % (location, config_loc))
                #turn MR output weight map into binary weight map and add it as
                #the first extension to the final MR.fits file
                MR_data = fits.getdata("%s/residuals/MR.fits" % (location))
                MR_header = fits.getheader("%s/residuals/MR.fits" % (location))
                MR_mask = fits.getdata("%s/residuals/MR_swarp_weight.fits" % (location))
                mask_median = np.median(MR_mask)
                mask_std = np.std(MR_mask)
                threshold = mask_median - (mask_std)
                MR_mask[MR_mask < threshold] = 0
                MR_mask[MR_mask >= threshold] = 1
                MR_hdu = fits.PrimaryHDU(MR_data, header=MR_header)
                MR_hdu_mask = fits.ImageHDU(MR_mask)
                MR_hdu_list = fits.HDUList([MR_hdu, MR_hdu_mask])
                MR_hdu_list.writeto("%s/residuals/MR.fits" % (location), overwrite=True)
                try:
                    os.remove("%s/residuals/MR_swarp_weight.fits" % (location))
                except:
                    print("\-> Error: Could not remove MR weight map\n")
            except:
                print("-> Error: Master residual construction failed\n")
    else:
        print("-> Error: Problem with number of residuals\n")        
        
def normalize(res):
    location = '/'.join(res.split('/')[:-2])
    template = glob.glob("%s/templates/*.fits" % (location))
    template = template[0]
    res_data = fits.getdata(res)
    res_mask = (fits.getdata(res, 1)-1)*-1
    res_data = np.ma.MaskedArray(res_data, mask=res_mask)
    image = res.replace('_A_residual_', '_A_')
    image = image.replace('residuals', 'data')
    try: im_median = float(fits.getval(image, 'MEDIAN'))
    except: im_median = np.median(np.ma.MaskedArray(fits.getdata(image), mask=np.logical_not(fits.getdata(image, 1))))
    try: template_median = float(fits.getval(template, 'MEDIAN'))
    except: template_median = np.median(np.ma.MaskedArray(fits.getdata(template), mask=np.logical_not(fits.getdata(template, 1))))
    res_noise = np.sqrt(im_median + template_median)
    norm_res_data = (res_data-(im_median-template_median))/res_noise
    norm_hdu = fits.PrimaryHDU(norm_res_data.data, header=fits.getheader(res))
    norm_mask = fits.ImageHDU(fits.getdata(res, 1))
    norm_list = fits.HDUList([norm_hdu, norm_mask])
    norm_list.writeto(res, overwrite=True)
    
def zeros_mask(location):
    residuals = glob.glob("%s/residuals/*_residual_.fits" % (location))
    for r in residuals:
        data = fits.getdata(r)
        hdr = fits.getheader(r)
        mask = fits.getdata(r, 1)
        try: weight_check = fits.getval(r, 'WEIGHT')
        except: weight_check = 'N'
        if weight_check == 'N':
            data = np.ma.MaskedArray(data, mask=mask)
            masked_data = np.ma.MaskedArray.filled(data, fill_value=0)
        elif weight_check == 'Y':
            data = np.ma.MaskedArray(data, mask=(mask-1)*-1)
            masked_data = np.ma.MaskedArray.filled(data, fill_value=0)
        else:
            print("\n-> Error: Can't find 'WEIGHT' keyowrd in residual FITS header\n-> Exiting...")
            sys.exit()
        hdu_data = fits.PrimaryHDU(masked_data.data, header=hdr)
        hdu_mask = fits.ImageHDU(mask)
        hdu_list = fits.HDUList([hdu_data, hdu_mask])
        hdu_list.writeto(r, overwrite=True)
    
def MR(path, method='swarp', sig_thresh=4, gauss_sig=3, gauss_filt=False, use_config_file=True):
    '''Stacks residual frames into a *master residual*. Extremely useful for identifying faint variables and quick object detection, but should be used with caution. See documentation for details.
    
    :param str path: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
    :param str method: Stacking method. 
    
        * *swarp* (default): Uses ``SWarp`` (Bertin) to stack the residuals according to the weighted average of the pixels.
        * *sos*: Sum of squares, pixel-wise.
        * *sos_abs*: Absolute sum of squares, pixel-wise. Preserves sign. Mathematically, this look like :math:`\Sigma(p_i * |p_i|)` with :math:`p_i` being the :math:`ith` pixel. For example, a series of pixels [10, 2, -3, -6] would be stacked according to 100 + 4 + -9 + -36.
        * *sigma_clip*: Takes the median of each pixel, unless there exists a pixel above or below a certain number of sigmas, in which case this outlying pixel is taken to be the stacked value.
    
    
    :param float sig_thresh: Only used for *sigma_clip* method. Number of sigmas pixel must exceed to be used as stacked value.
    :param float gauss_sig: Only used for *sigma_clip* method. Number of sigmas used for gaussian filter.
    :param bool gauss_filt: Only used for *sigma_clip* method. When ``True`` the final master residual will be smoothed with a gaussian filter with a sigma equal to *gauss_sig*.
    :param bool use_config_file: If ``True`` all input parameters are fetched from the local *OASIS.config* file.
    :returns: A stacked master residual frame, located in the **residuals** directory with the name *MR.fits*.
    
    '''
    paths = (path.replace(' ','')).split(',')
    del path
    for path in paths:
        if use_config_file == True:
            method = initialize.get_config_value('MR_method')
        if method == 'sos' or method == 'sos_abs' or method == 'sigma_clip':
            MR_other(path, mode=method, sigma_thresh=sig_thresh, gauss_sigma=gauss_sig, gauss_filter=gauss_filt)
        elif method == 'swarp':
            MR_swarp(path)
        else:
            print("\n-> Error: Unrecognized method\n-> Please enter either 'swarp', 'sos', 'sos_abs', or 'sigma_clip'\n-> Exiting...")
    
if __name__ == '__main__':
    path = input("\n-> Enter path to exposure time directory: ")
    MR_method = input("-> Master residual construction method (swarp/sos/sos_abs/sigma_clip): ")
    MR(path, method=MR_method)