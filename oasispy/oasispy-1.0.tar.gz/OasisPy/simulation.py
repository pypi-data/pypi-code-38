#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 15:45:30 2018

@author: andrew
"""

import os
import glob
from astropy.io import fits
import numpy as np
import shutil
from initialize import loc
from initialize import create_configs
from psf import fwhm
import make_stars
import sex
from psf import psfex, get_first_model
import sys
from tabulate import tabulate
from scipy.ndimage import rotate, shift
from astropy.convolution import Gaussian2DKernel, Moffat2DKernel
import pipeline
import subtract

loc = '/media/andrew/SDI'

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    sys.exit()

def sim_fakes(location, n_fakes=20, iterations=50, input_mode='flux', PSF='moffat', subtract_method='ois', f_min=0, f_max=40000):
    '''Simulates transient signals (fakes) and tests **OASIS**'s ability to detect them. The procedure of the simulation is as follows:
        
            1. Makes a copy of the specified data set and moves it to the **simulations** directory.
            2. Chooses a random image out of the data set and adds in fakes.
            3. Runs the data set through the **OASIS Pipeline**.
            4. Outputs a catalog of all fakes and whether or not they were detected.
            5. Simulation is repeated with a different set of fakes.
            
            :param str location: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
            :param int n_fakes: Number of fakes added to the chosen image.
            :param int iterations: Number of iterations the simulation goes through. The total number of fakes added is then :math:`n\_fakes * iterations`. It is reccommended to choose *n_fakes* and *iterations* such that the total number of fakes is high, at least a few hundred, ideally more than 1000.
            :param str input_mode: How to interpret fake's flux parameter.
            
                * *flux* (default): Fake's brightness is assumed to be total flux of the fake in ADU and is determined by *f_min* and *f_max* parameters.
                * *mag*: Fake's brightness is given in magnitudes instead of ADU flux. *f_min* and *f_max* are then assumed to be apparent magnitudes rather than ADU counts.
            
            :param str PSF: Type of PSF model used for fake construction. See documentation for details.
            
                * *moffat* (default): Fakes are convolved with a 2D Moffat kernel.
                * *gaussian*: Fakes are convolved with a symmetric 2D Gaussian kernel.
                
            :param str subtract_method: Subtraction method used, can be either *ois* or *hotpants*, default is *ois*. See ``subtract`` method's documentation for details.
            :param float f_min: Minimum flux for fakes. Assumed to either be given in ADU counts or apparent magnitudes depending on *input_mode*.
            :param float f_max: Maximum flux for fakes. Assumed to either be given in ADU counts or apparent magnitudes depending on *input_mode*.
            :returns: Catalog of all fakes, the image they were added to, iteration, and whether or not they were detected. See documentation for details.
    
    '''
    try:
        #pick a random image in location dataset to use as the fake
        dataImages = glob.glob(location + '/data/*.fits')
        imIndex = np.random.randint(low=0, high=(len(dataImages)-1))
        image = dataImages[imIndex]
        tarIndex = len(loc.split('/'))
        target = location.split('/')[tarIndex+2:tarIndex+3]
        target = target[0]
        #copy data to simulations directory
        check = loc + '/OASIS/simulations/' + target
        if os.path.exists(check) == False:
            copy_to_sim(target)
        #rename image paths to correspond to simulations directory
        image = image.replace('targets', 'simulations')
        image_name = image.split('/')[-1]
        length = len(image_name) + 6
        location = image[:-length]
        location = location.replace(target, "%s_fakes" % (target))
        image = image.replace(target, "%s_fakes" % (target))
    #    #copy image to be faked to exposure time directory so it can be retrieved
    #    os.system('cp %s %s' % (image, location))
        #define location of simulation results files
        fake_txt = location + '/results_fake.txt'
        MR_txt = location + '/results_MR.txt'
        #get PSF FWHM of original input image
        if os.path.exists(image.replace('data','psf')[:-4]+'cat') == False:
            sex.sextractor_psf_sim(location, image)
            psfex(location)    
        FWHM = fwhm(image)
        #get input image data and header
        image_hdu = fits.open(image)
        image_header = image_hdu[0].header
        image_data = image_hdu[0].data
        image_mask = image_hdu[1].data
        image_hdu.close()
        shape = image_data.shape
        #move fake image to configs directory
        os.system("mv %s %s/configs" % (image, location))
        #redefine location of image
        image_new_loc = image.replace('data', 'configs')
        #convert input mags to fluxes
        if input_mode == 'mag':
            f_min = mag_to_flux(image, f_min)
            f_max = mag_to_flux(image, f_max)
        fake_name = image
        #perform simulation for 'iterations' number of loops
        for i in range(iterations):
            #define blank results slates
            fake_results = []
            MR_results = []
            #delete all previous simluations data
            clear_image(image)
            #make 'n_fakes' fluxes
            print("-> Creating fakes...")
            flux_scales = np.random.random(n_fakes)
            flux = ((f_max-f_min)*flux_scales) + f_min
            x = [round(shape[0]*np.random.random()) for i in range(n_fakes)]
            y = [round(shape[1]*np.random.random()) for j in range(n_fakes)]
            #print fake sources' info
            print("-> Fake fluxes: \n" + "-> " + str(flux))
            print("-> Fake x: \n" + "-> " + str(x))
            print("-> Fake y: \n" + "-> " + str(y))
            print("-> Fake PSF: %s" % (PSF))
            print("-> Fake FWHM: %.3f\n" % (FWHM))
            if PSF == 'gaussian':
                #make fake image with Gaussian profile
                print("-> Gaussian smearing fakes...")
                gaussian_kernel_1 = Gaussian2DKernel(x_stddev=(FWHM/2.355), y_stddev=(FWHM/2.355))
                gaussian_kernel_2 = Gaussian2DKernel(x_stddev=((FWHM*2)/2.355), y_stddev=((FWHM*2)/2.355))
                conv_kernel = (0.9*gaussian_kernel_1) + (0.1*gaussian_kernel_2)
                fake = make_stars.make_image(shape[0], shape[1], x_loc=x, y_loc=y, fluxes=flux, psf=[conv_kernel])
            elif PSF == 'moffat':
                print("-> Moffat smearing fakes...")
                #define Moffat convolution kernel
                conv_kernel = Moffat2DKernel(gamma=make_stars.get_moffat_gamma(FWHM), alpha=4.765)
                #make image using fluxes na dpositions defined earlier, then convolve with above kernel
                fake = make_stars.make_image(shape[0], shape[1], x_loc=x, y_loc=y, fluxes=flux, psf=[conv_kernel])
            #add fake to original image and overwrite the OG fits file
            print("-> Adding fake to original image...")
            fake += image_data
            hduData = fits.PrimaryHDU(fake, header=image_header)
            hduMask = fits.ImageHDU(image_mask)
            hduList = fits.HDUList([hduData, hduMask])
            hduList.writeto(fake_name, overwrite=True)
            #run images through pipeline
            subtract.subtract_run(location, method=subtract_method)
            #run SExtractor on only fake image
            sex.sextractor_sim(fake_name.replace('_N_', '_A_'))
            #run SExtractor also on master residual to look for fakes
            sex.sextractor_MR(location)
            #find any fakes that were detected by SExtractor in fake catalog
            with open(location+'/sources/filtered_sources.txt', 'r') as src:
                detects = src.readlines()
                src.close()
            for n in range(n_fakes):
                found = 0
                for d in detects:
                    try:
                        float(d.split()[0])
                        if (y[n]-2)<float(d.split()[2])<(y[n]+2) and (x[n]-2)<float(d.split()[3])<(x[n]+2):
                            found += 1
                    except:
                        pass
                fake_results.append([i,image_name,x[n],y[n],flux[n],found])
            #write simulation results to fake_results.txt file
            with open(fake_txt, 'a+') as sim_data:
                sim_data.writelines(tabulate(fake_results))
                sim_data.close()
            #find any fakes that were detected by SExtractor in MR catalog
            with open(location+'/sources/MR_sources_filtered.txt', 'r') as src:
                detects = src.readlines()
                src.close()
            for n in range(n_fakes):
                found = 0
                for d in detects:
                    try: 
                        float(d.split()[0])
                        if (y[n]-2)<float(d.split()[2])<(y[n]+2) and (x[n]-2)<float(d.split()[3])<(x[n]+2):
                            found += 1
                    except:
                        pass
                MR_results.append([i,image_name,x[n],y[n],flux[n],found])
            #write simulation results to MR_results.txt file
            with open(MR_txt, 'a+') as sim_data:
                sim_data.writelines(tabulate(MR_results))
                sim_data.close()
        #move fake image from configs back to data directory
        os.system("mv %s %s/data" % (image_new_loc, location))
    except KeyboardInterrupt:
        print('\n-> Interrupted-- Exiting..')
        try:
            clear_image(image)
            os.system("mv %s %s/data" % (image_new_loc, location))
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        
def clear_contents(location):
    PSF = location + '/psf'
    residuals = location + '/residuals'
    sources = location + '/sources'
    templates = location + '/templates'
    group = [PSF,residuals,sources,templates]
    for g in group:
        for the_file in os.listdir(g):
            file_path = os.path.join(g, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

def clear_image(image):
    print('-> Removing old simulation files...')
    image_name = image.split('/')[-1]
    location = image.split('/')[:-2]
    location = '/'.join(location)
    sources = glob.glob("%s/sources/*" % (location))
    residuals = glob.glob("%s/residuals/*%sresidual_.fits" % (location, image_name[:-5]))
    master_res = glob.glob("%s/residuals/MR.fits" % (location))
    del_files = sources+residuals+[image]+master_res
    for d in del_files:
        try:
            os.remove(d)
        except:
            pass

def flux_to_mag(image, flux):
    zp = 0
    mag = 0
    zp_g = 0
    zp_i = 0
    zp_loc = os.path.dirname(make_stars.__file__) + '/config/lco_zero_points.txt'
    with open(zp_loc, 'r') as zpoint:
        zp_data = zpoint.readlines()
        zpoint.close()
    for i in range(len(zp_data)):
        zp_data[i] = zp_data[i].split()
    hdu = fits.open(image)
    site = hdu[0].header['SITEID']
    tel = hdu[0].header['TELID'][-1]
    camera = hdu[0].header['INSTRUME'][1]
    fltr = hdu[0].header['FILTER']
    exp = float(hdu[0].header['EXPTIME'])
    gain = float(hdu[0].header['GAIN'])
    if fltr == 'g' or fltr == 'i':
        params = [site, tel, camera, fltr]
        for j in range(len(zp_data)):
            if params == zp_data[j][:4]:
                zp = float(zp_data[j][4])
        if zp != 0:
            mag = (-2.5*np.log10(flux/(gain*exp))) + zp
    else:
        params_g = [site, tel, camera, 'g']
        params_i = [site, tel, camera, 'i']
        for j in range(len(zp_data)):
            if params_g == zp_data[j][:4]:
                zp_g = float(zp_data[j][4])
            elif params_i == zp_data[j][:4]:
                zp_i = float(zp_data[j][4])
        if zp_g != 0 and zp_i != 0:
            zp = -2.5*np.log10((10**(-0.4*zp_g)) + (10**(-0.4*zp_i)))
            mag = (-2.5*np.log10(flux/(gain*exp))) + zp
    if zp==0 and zp_g==0 and zp_i==0:
        print("-> Error: Could not find matching zero points...")
    if mag != 0:
        return mag

def mag_to_flux(image, mag):
    '''
    converts magnitudes to net photon flux from a source for a given site/telescope
    '''
    zp = 0
    zp_g = 0
    zp_i = 0
    flux = 0
    zp_loc = os.path.dirname(make_stars.__file__) + '/config/lco_zero_points.txt'
    with open(zp_loc, 'r') as zpoint:
        zp_data = zpoint.readlines()
        zpoint.close()
    for i in range(len(zp_data)):
        zp_data[i] = zp_data[i].split()
    hdu = fits.open(image)
    site = hdu[0].header['SITEID']
    tel = hdu[0].header['TELID'][-1]
    camera = hdu[0].header['INSTRUME'][1]
    fltr = hdu[0].header['FILTER']
    exp = float(hdu[0].header['EXPTIME'])
    gain = float(hdu[0].header['GAIN'])
    if fltr == 'g' or fltr == 'i':
        params = [site, tel, camera, fltr]
        for j in range(len(zp_data)):
            if params == zp_data[j][:4]:
                zp = float(zp_data[j][4])
        if zp != 0:
            flux = (10**((mag-zp)/(-2.5)))*gain*exp
    else:
        params_g = [site, tel, camera, 'g']
        params_i = [site, tel, camera, 'i']
        for j in range(len(zp_data)):
            if params_g == zp_data[j][:4]:
                zp_g = float(zp_data[j][4])
            elif params_i == zp_data[j][:4]:
                zp_i = float(zp_data[j][4])
        if zp_g != 0 and zp_i != 0:
            zp = -2.5*np.log10((10**(-0.4*zp_g)) + (10**(-0.4*zp_i)))
            flux = (10**((mag-zp)/(-2.5)))*gain*exp
    if zp==0 and zp_g==0 and zp_i==0:
        print("-> Error: Could not find matching zero points...")
    if flux != 0:
        return flux

def copy_to_sim(tar, mode='fakes', image=''):
    '''make a copy of target directory in the simulations directory
    "fakes" mode copies all files to simulations directory
    "samefield" mode copies only the image that will be used for zero-point simulation
    '''
    sim_path = loc + "/OASIS/simulations"
    tar_dir_path = loc + "/OASIS/targets"
    #delete any existing simulation data
    try:
        shutil.rmtree("%s/%s" % (sim_path, tar))
        print("-> Deleting any existing simulation data...")
    except Exception as e:
        print(e)
    if mode == 'fakes':
        try:
            print("-> Copying target directory created in simulations directory...")
            shutil.copytree(tar_dir_path + "/" + tar, sim_path + "/" + tar + "_fakes")
        except Exception as e:
            print(e)
    elif mode == 'samefield':
        try:
            if image == '':
                print("-> Error: Need to define zero-point image\n-> Exiting...")
                sys.exit()
            print("-> Copying zero-point image to simulations directory...")
            location = image.split('/')[:-2]
            location = '/'.join(location)
            location = location.replace(tar_dir_path, '')
            image_psf = image.replace('fits', 'psf')
            image_psf = image_psf.replace('data', 'psf')
            image_cat = image.replace('fits', 'cat')
            image_cat = image_cat.replace('data', 'psf')
            os.system("mkdir -p %s%s/data && cp %s %s%s/data" % (sim_path, location, image, sim_path.replace(tar, tar+"_zeropoint"), location))
            os.system("mkdir -p %s%s/psf && cp %s %s%s/psf" % (sim_path, location, image_psf, sim_path, location))
            os.system("cp %s %s%s/psf" % (image_cat, sim_path, location))
            # try to create exposure time file tree
            try:
                os.mkdir("%s%s/templates" % (sim_path, location))
                os.mkdir("%s%s/sources" % (sim_path, location))
                os.mkdir("%s%s/residuals" % (sim_path, location))
            except:
                pass
        except Exception as e:
            print(e)

def fake_dir(location):
    '''
    create fakes directory for a given target
    '''
    fake_dir = location + "/fakes"
    if os.path.exists(fake_dir) == False:
        os.mkdir(fake_dir)
    else:
        print("Fakes directory already exists for this target")

def sim_sameField(location, mode='moffat', numIms=100, bkg_mag=22.5, fwhm_min=3, fwhm_max=6, 
                  rot_min=-2.5, rot_max=2.5, shift_min=-2, shift_max=2, scale_mult=(0,1.5),
                  scale_add=(-20,50), zero_point=25):
    '''Test **OASIS**'s ability to handle frame-by-frame variations in astronomical data and filter out false-positive sources. The procedure of the simulation is as follows:
        
        1. Copies a random science image from the specified dataset to the **simulations** directory.
        2. A source catalog of the chosen science image is made, containing information on each source's centroid location and total flux.
        3. Using this source catalog, simulations of the chosen science image are made, all with constant source flux and location, but with different backgrounds, seeing, and pointing.
        4. The set of simulated images are sent through the **OASIS Pipeline**.
        5. Low numbers of detected sources signifies a successful simulation. There are no variable objects in the simulated images, so ideally zero sources should be detected by **OASIS**.
        
        :param str location: Path of data file tree (contains the **configs**, **data**, **psf**, **residuals**, **sources**, **templates** directories). Use a comma-separated list for mapping to multiple datasets.
        :param str mode: Simulation mode. Method by which simulated images are made. All images are given a uniform background, then smeared according to Poisson statistics.
        
            * *moffat* (default): Sources are convolved with a 2D Moffat kernel.
            * *gauss*: Sources are convolved with a symmetric 2D Gaussian kernel.
            * *real*: The actual PSF model of the chosen science image is used as the convolution kernel.
            * *sky*: AstrOmatic program ``SkyMaker`` (Bertin) is used to make simulated images.
            
        :param int numIms (default=100): Number of simulated images to make.
        :param float bkg_mag: Average background level in mags. Actual simulated background levels are chosen to be a random value within the interval :math:`[bkg\_mag-1.5, bkg\_mag+1.5]`.
        :param float fwhm_min: Minimum FWHM of simulated images in pixels.
        :param float fwhm_max: Maximum FWHM of simulated images in pixels.
        :param float rot_min: Lower bound on angle of rotation in degrees.
        :param float rot_max: Upper bound on angle of rotation in degrees.
        :param float shift_min: Lower bound on (X,Y) shift in pixels.
        :param float shift_max: Upper bound on (X,Y) shift in pixels.
        :param tuple scale_mult: Interval of acceptable multiplicative scale factors.
        :param tuple scale_add: Interval of acceptable additive scale factors.
        :param float zero_point: Zero point magnitude.
        :returns: Standard **OASIS Pipeline** output, residual frames located in **residuals** and source catalogs located in **sources**.
        
    '''
    ref_im = glob.glob(location + '/data/*_ref_A_.fits')
    if os.path.exists(location) == False:
        print("-> Error: Problem with path name(s)-- make sure paths exist and are entered correctly\n-> Exiting...")
        sys.exit()
    if len(ref_im) != 1:
        print("-> Error: Problem with number of reference images\n-> Exiting...\n")
        sys.exit()
    ref_im = ref_im[0]
    ref_fwhm = fwhm(ref_im)
    path_splits = ref_im.split('/')
    image_name = path_splits[-1]
    sim_loc = location.replace('targets', 'simulations')
    len_loc = len(loc.split('/'))
    tar = path_splits[len_loc+2]
    copy_to_sim(tar, image=ref_im, mode='samefield')
    ref_psf = glob.glob("%s/psf/*_ref_A_.psf" % (sim_loc))
    if len(ref_psf) != 1:
        print("-> Error: Problem with number of reference PSF files\n-> Exiting...\n")
        sys.exit()
    try:
        clear_contents(sim_loc)
    except:
        pass
    images = glob.glob("%s/data/*.fits" % (sim_loc))
    ref_im_sim = ref_im.replace("targets", "simulations")
#delete all original images except reference
    for i in images:
        name = i.split('/')[-1]
        if name != image_name:
            os.remove(i)
#create configs directory if none exists
    create_configs(sim_loc)
#make source catalog of reference using SExtractor
    sim_config = "%s/configs/default_sim.sex" % (sim_loc)
    sim_params = "%s/configs/default_param_sim.sex" % (sim_loc)
    with  open(sim_config, 'r') as conf:
        lines = conf.readlines()
    lines[6] = "CATALOG_NAME" + "        " + "%s/data/reference.cat" % (sim_loc) + "\n"
    lines[9] = "PARAMETERS_NAME" + "        " + sim_params + "\n"
    lines[22] = "FILTER_NAME" + "        " + "%s/configs/default.conv" % (sim_loc) + "\n"
    lines[70] = "SEEING_FWHM" + "        " + str(ref_fwhm) + "\n"
    lines[127] = "PSF_NAME" + "        " + ref_psf[0] + "\n"
    with open(sim_config, 'w') as conf_write:
        conf_write.writelines(lines)
    os.system("sextractor %s[0] -c %s" % (ref_im_sim, sim_config))
#extract x_pos, y_pos, and fluxes from SExtractor catalog
    ref_cat = "%s/data/reference.cat" % (sim_loc)
    with open(ref_cat, 'r') as cat:
        cat_lines = cat.readlines()
#get simulated image's metadata
    ref_hdu = fits.open(ref_im_sim)
    ref_data = ref_hdu[0].data
    ref_header = ref_hdu[0].header
    ref_mask = ref_hdu[1].data
    try: weight_check = fits.getval(ref_im_sim, 'WEIGHT')
    except: weight_check = 'N'
    if weight_check == 'Y':
        ref_mask = (ref_mask-1)*-1
    ref_mask = ref_mask.astype(np.int64)
    ref_hdu.close()
    from astropy.stats import sigma_clipped_stats
    mean, median, std = sigma_clipped_stats(ref_data, sigma=3.0)
#extract simulated image's source information from SExtractor catalog
    x_pos = []
    y_pos = []
    flux = []
    for c in cat_lines:
        splits = c.split()
        if splits[0] != '#':
            flux.append(float(splits[0]))
            x_pos.append(round(float(splits[3])))
            y_pos.append(round(float(splits[4])))
#if mode is set to use SkyMaker for making the simulations, configure SkyMaker
    if mode == 'sky':
        mags = []
        for f in flux:
            mags.append((28-(np.log(f))))
        with open("%s/configs/sky_list.txt" % (sim_loc), "w+") as sky_list:
            for i in range(len(flux)):
                sky_list.write("100 %.3f %.3f %.3f\n" % (x_pos[i], y_pos[i], mags[i]))
        #get pixel scale of reference image
        pixscale = float(ref_header['PIXSCALE'])
        #define oversampling
        oversample = pixscale*25
        #define sky.config location
        sky_config = "%s/configs/sky.config" % (sim_loc)
#start making fake images
    print("\n-> Making simulated images...")
    for n in range(numIms):
#define image name
        if n == 0:
            image_name = '%s/data/%d_ref_A_.fits' % (sim_loc, n)
        else:
            image_name = '%s/data/%d_N_.fits' % (sim_loc, n)
#for each image: make sources w/ random fwhm b/w (3,6), rotate/zoom, shift, add a different gaussian dist. of noise, change scale linearly, poisson smear
        #define FWHM of simulation
        image_fwhm = ((fwhm_max-fwhm_min) * np.random.random()) + fwhm_min
        if n == 0:
            image_fwhm = ref_fwhm
        #based on the mode chosen, create the corresponding convolution kernel and make simulated image
        if mode != 'sky':
            if mode == 'moffat':
                moffat_kernel_1 = Moffat2DKernel(gamma=make_stars.get_moffat_gamma(image_fwhm), alpha=7)
                moffat_kernel_2 = Moffat2DKernel(gamma=make_stars.get_moffat_gamma(image_fwhm), alpha=2)
                conv_kernel = (0.8*moffat_kernel_1) + (0.2*moffat_kernel_2)
            elif mode == 'gauss':
                gaussian_kernel_1 = Gaussian2DKernel(x_stddev=(image_fwhm/2.355), y_stddev=(image_fwhm/2.355))
                gaussian_kernel_2 = Gaussian2DKernel(x_stddev=((image_fwhm*2)/2.355), y_stddev=((image_fwhm*2)/2.355))
                conv_kernel = (0.9*gaussian_kernel_1) + (0.1*gaussian_kernel_2)
            elif mode == 'real':
                conv_kernel = get_first_model(ref_im)
            try:
                norm = np.linalg.norm(conv_kernel)
                if norm != 0: 
                    conv_kernel /= norm
            except:
                pass
            image = make_stars.make_image(ref_data.shape[0], ref_data.shape[1], 
                                      x_loc=y_pos, y_loc=x_pos, fluxes=flux, psf=[conv_kernel])
        #if mode is set to 'sky' use SkyMaker to make simulated image
        elif mode == 'sky':
            bkg_Mag = (1.5*np.random.random()) + bkg_mag
            image_fwhm_arcsec = image_fwhm*pixscale
            with open(sky_config, 'r') as sky:
                sky_lines = sky.readlines()
            sky_lines[6] = "IMAGE_NAME" + "        " + image_name + "\n"
            sky_lines[7] = "IMAGE_SIZE" + "        " + str("%d, %d" % (ref_data.shape[1], ref_data.shape[0])) + "\n"
            sky_lines[19] = "SATUR_LEVEL" + "        " + str(ref_header['SATURATE']) + "\n"
            sky_lines[21] = "EXPOSURE_TIME" + "        " + str(ref_header['EXPTIME']) + "\n"
            sky_lines[26] = "PIXEL_SIZE" + "        " + str(pixscale) + "\n"
            sky_lines[34] = "SEEING_FWHM" + "        " + str(image_fwhm_arcsec) + "\n"
            sky_lines[37] = "PSF_OVERSAMP" + "        " + str(oversample) + "\n"
            sky_lines[65] = "BACK_MAG" + "        " + str(bkg_Mag) + "\n"
            with open(sky_config, 'w') as sky:
                sky.writelines(sky_lines)
            os.system("sky %s/configs/sky_list.txt -c %s" % (sim_loc, sky_config))
            try:
                os.remove("%s/data/%s.list" % (sim_loc, image_name[:-5]))
            except:
                pass
            image = fits.getdata(image_name)
        else:
            print("-> Error: Please enter a valid mode (gauss, moffat, sky, real)\n-> Exiting...")
            sys.exit()
        #now we start the warping of each simulation
        #first rotate/zoom (angle is random b/w 0 and 30 degrees, zoom is random b/w 0 and 2)
        if n != 0:
            #define initial mask for each simulation
            Mask = np.zeros(image.shape)
            rot_angle = ((rot_max-rot_min)*np.random.random())+rot_min
            dx = (shift_max-shift_min) * np.random.random() - shift_min
            dy = (shift_max-shift_min) * np.random.random() - shift_min
            image = rotate(image, rot_angle, reshape=False)
            image = shift(image, [dx,dy])
            Mask = rotate(ref_mask, rot_angle, reshape=False, cval=1)
            Mask = shift(Mask, [dx,dy], cval=1)
        else:
            Mask = ref_mask
        #for non-SkyMaker simulations, add in a random background, poisson smear the image, and rescale it
        if mode != 'sky':
            #add constant background
            bkg_loc = 2.512**(zero_point - bkg_mag)
            bkg_scl = ((std+5)-(std-5))*np.random.random()+(std-5)
            bkg = np.random.normal(loc=bkg_loc, scale=bkg_scl, size=image.shape)
            image = np.add(image, bkg)
            #poisson smear
            negative_image = np.zeros(image.shape)
            negative_image[:] = image[:]
            image[image < 0] = 0
            negative_image[negative_image > 0] = 0
            image = np.random.poisson(image)
            image = image.astype(np.float64)
            negative_image *= -1
            negative_image = np.random.poisson(negative_image)
            negative_image = negative_image.astype(np.float64)
            negative_image *= -1
            image += negative_image
            #rescale image linearly
            a = ((scale_mult[1] - scale_mult[0])*np.random.random()) + scale_mult[0]
            b = (scale_add[1] - scale_add[0])*np.random.random() - scale_add[0]
            image *= a
            image += b
        #write new image to data folder in target's simulations folder
        newHDUData = fits.PrimaryHDU(image, header=ref_header)
        newHDUMask = fits.ImageHDU(Mask)
        newHDUList = fits.HDUList([newHDUData, newHDUMask])
        newHDUList.writeto(image_name, overwrite=True)
        newHDU = fits.open(image_name, mode='update')
        (newHDU[0].header).set('WEIGHT', 'N')
        (newHDU[0].header).set('SCALED', 'N')
        newHDU.close()
    os.system("mv %s %s" % (ref_im_sim, sim_loc))
    os.system("mv %s %s" % (ref_psf, sim_loc))
    os.system("mv %s %s.cat" % (ref_psf[:-4], sim_loc))
    if mode == 'sky':
        sim_lists = glob.glob("%s/data/*.list" % (sim_loc))
        for sl in sim_lists:
            os.remove(sl)
    pipeline.pipeline_run_sim(sim_loc)
        
def SIM():
    '''
    Master simulation function. Allows users to choose simulation type and supply all other simulation parameters.
    '''
    sim_mode = input("\n-> Simulation mode (fake/zero point): ")
    if sim_mode == 'fake':
        sim_location = input("-> Path(s) of exposure time directory of images to be simulated: ")
        sim_location = sim_location.replace(' ','')
        sim_location = sim_location.split(',')
        num_fakes = input("-> Number of fake sources added: ")
        num_iter = input("-> Number of iterations: ")
        psf_choice = input("-> PSF of fakes (moffat/gaussian): ")
        flux_min = input("-> Minimum fake flux in photons (default=0): ")
        if flux_min == '':
            flux_min = 0
        flux_max = input("-> Maximum fake flux in photons (default=50000): ")
        if flux_max == '':
            flux_max = 50000
        for s in sim_location:
            sim_fakes(s, int(num_fakes), int(num_iter), PSF=psf_choice, f_min=float(flux_min), f_max=float(flux_max))
    elif sim_mode == 'zero point':
        sim_location = input("-> Path(s) of exposure time directory of images to be simulated: ")
        sim_location = sim_location.replace(' ','')
        sim_location = sim_location.split(',')
        num_im = input("-> Number of images to make: ")
        sim_mode = input("-> Simulation mode (moffat/gauss/real/sky): ")
        bkg = input("-> Average background in mags (default=22.5): ")
        if bkg == '':
            bkg = 22.5
        fwhmMin = input("-> FWHM lower bound (default=3): ")
        if fwhmMin == '':
            fwhmMin = 3
        fwhmMax = input("-> FWHM upper bound (default=6): ")
        if fwhmMax == '':
            fwhmMax = 6
        rotMin = input("-> Minimum rotation angle in degrees (default=-2.5): ")
        if rotMin == '':
            rotMin = -2.5
        rotMax = input("-> Maximum rotation angle in degrees (default=2.5): ")
        if rotMax == '':
            rotMax = 2.5  
        shiftMin = input("-> Minimum X and Y shift in pixels (default=-2): ")
        if shiftMin == '':
            shiftMin = -2
        shiftMax = input("-> Maximum X and Y shift in pixels (default=2): ")
        if shiftMax == '':
            shiftMax = 2        
        if sim_mode != 'sky':
            scl_mult = input("-> Multiplicative scale factor random interval (default=(0,1.5)): ")
            if scl_mult == '':
                scl_mult = '(0, 1.5)'
            scl_add = input("-> Additive scale factor random interval (default=(-20,50)): ")
            if scl_add == '':
                scl_add = '(-20, 50)'
            zp = input("-> Zero point magnitude (default=25): ")
            if zp == '':
                zp = 25
            for s in sim_location:
                sim_sameField(s, numIms=int(num_im), bkg_mag=float(bkg), fwhm_min=float(fwhmMin), 
                              fwhm_max=float(fwhmMax), rot_min=float(rotMin),
                              rot_max=float(rotMax), shift_min=float(shiftMin),
                              shift_max=float(shiftMax), scale_mult=eval(scl_mult), scale_add=eval(scl_add),
                              zero_point=float(zp), mode=sim_mode)
        else:
            for s in sim_location:
                sim_sameField(s, numIms=int(num_im), bkg_mag=float(bkg), fwhm_min=float(fwhmMin), 
                              fwhm_max=float(fwhmMax), rot_min=float(rotMin),
                              rot_max=float(rotMax), shift_min=float(shiftMin),
                              shift_max=float(shiftMax), mode=sim_mode)      
    else:
        print("-> Error: Unknown input\n-> Exiting...")
        sys.exit()
        
if __name__ == '__main__':
    SIM()