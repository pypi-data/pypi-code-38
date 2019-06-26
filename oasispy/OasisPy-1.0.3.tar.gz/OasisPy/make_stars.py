#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 15:18:38 2018

@author: andrew
"""

import numpy as np
from astropy.convolution import convolve
from astropy.table import Table
from photutils.datasets import make_gaussian_sources_image

def make_sources(x_size, y_size, num_sources, psf=[], flux=50000):
    image_size = (x_size, y_size)
    
    num = num_sources
    fluxes = flux*np.random.random(size=num)
    
    image = np.zeros(image_size)
    
    for i in range(num):
        x_loc, y_loc = np.random.randint(0,x_size), np.random.randint(0,y_size)
        image[x_loc][y_loc] = fluxes[i]
        
    for p in psf:
        image = convolve(image, p)
    
    return image, x_loc, y_loc, fluxes

def make_image(size_x, size_y, x_loc=[], y_loc=[], fluxes=[], psf=[]):
    image = np.zeros((size_x, size_y))
    num_sources = len(fluxes)
    for source in range(num_sources):
        image[x_loc[source]-1][y_loc[source]-1] = fluxes[source]
    
    for p in psf:
        image = convolve(image, p)
    
    return image

def get_moffat_gamma(fwhm, alpha=4.765):
    gamma = fwhm/(2*np.sqrt(2**(1/alpha)-1))
    return gamma

def make_gaussian_im(x_size, y_size, fluxes=[100,1000,10000], x_pos=[500,250,750], y_pos=[300,80,460],std=[6,6,6]):
    shape = (x_size, y_size)
    table = Table()
    table['flux'] = fluxes
    table['x_mean'] = x_pos
    table['y_mean'] = y_pos
    table['x_stddev'] = std
    table['y_stddev'] = std
    image = make_gaussian_sources_image(shape, table)
    return image