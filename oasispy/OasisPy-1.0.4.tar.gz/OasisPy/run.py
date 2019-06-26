#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:45:48 2018

@author: andrew
"""

def RUN():
    '''
    Master run function. Allows user to call any of the main **OASIS** methods. See documentation for details.
    '''
    print('\n\t ------------------------------------------------------')
    print('\t                     OASIS  v.1.0                       ')
    print('\n\t  Difference Imaging Software for Optical SETI Purposes  ')
    print('\t           Developed for the SDI Program @ UCSB          ')
    print('\t              http://www.deepspace.ucsb.edu              ')
    print('\n\t Contact andrew.henry.stewart@emory.edu for bug reports  ')
    print('\t ------------------------------------------------------')
    print("\n-> Methods:")
    print("\n\tinitialize    get        mask        align")
    print("\tpsf           combine    subtract    mr")
    print("\textract       pipeline   simulate    test")
    method = str(input('\n-> Enter method: '))
    if method == 'get':
        import get
        get.GET()
    elif method == 'mask':
        path = input("-> Enter path to exposure time directory: ")
        import mask
        mask.MASK(path)
    elif method == 'align':
        path = input("-> Enter path to exposure time directory: ")
        import align
        align.ALIGN(path)
    elif method == 'psf':
        path = input("-> Enter path to exposure time directory: ")
        import psf
        psf.PSF(path)
    elif method == 'combine':
        path = input("-> Enter path to exposure time directory: ")
        import combine
        combine.COMBINE(path)
    elif method == 'subtract':
        path = input("-> Enter path to exposure time directory: ")
        import subtract
        subtract.SUBTRACT(path)
    elif method == 'mr':
        path = input("-> Enter path to exposure time directory: ")
        import MR
        MR.MR(path)
    elif method == 'extract':
        import extract
        path = input("-> Enter path to exposure time directory: ")
        extract_method = input("\n-> Extract method (both/indiv/MR): ")
        extract.EXTRACT(path, method=extract_method)
    elif method == 'pipeline':
        import pipeline
        path = input("-> Enter path to exposure time directory: ")
        pipeline.PIPELINE(path)
    elif method == 'initialize':
        import initialize
        initialize.INITIALIZE()
    elif method == 'test':
        import test
        test.TEST()
    elif method == 'simulate':
        import simulation
        simulation.SIM()
    else:
        print("-> Error: Method not recognized")

if __name__ == '__main__':
    RUN()