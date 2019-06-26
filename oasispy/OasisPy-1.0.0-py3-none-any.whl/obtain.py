#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:54:19 2018

@author: andrew
"""

import os
import zipfile
from astropy.io import fits
import glob
from initialize import loc
from initialize import create
import gzip

def move(download_loc):
    '''
    move downloaded LCO data from download_loc to temp folder
    '''
    temp = "%s/OASIS/temp" % (loc)
    num = 1
    x = []
    y = []
    for root, dirs, files in os.walk(download_loc):
        for f in files:
            if f[:3] == "lco":
                os.system('mv "%s/%s" %s' % (download_loc, f, temp))
                x.append(num)
        for d in dirs:
            if d[:3] == "lco":
                os.system('mv "%s/%s" %s' % (download_loc, d, temp))
                y.append(num)
    print("-> moved %d files and %d directories from %s to /OASIS/temp\n" % (sum(x), sum(y), download_loc))

def process():
    '''
    unzips and funpacks downloaded LCO data in temp directory
    '''
    num = 1
    x = []
    y = []
    d = 0
    temp = "%s/OASIS/temp" % (loc)
    zipfiles = glob.glob("%s/*.zip" % (temp))
    for i in zipfiles:
        try:
            zip_ref = zipfile.ZipFile(i, 'r')
            zip_ref.extractall(temp)
            zip_ref.close()
            os.remove(i)
            x.append(num)
            d =+ 1
        except:
            print("-> Unable to unzip using zipfile, trying with Gzipfile...")
            try:
                zip_ref = gzip.GzipFile(i, 'r')
                zip_ref.extractall(temp)
                zip_ref.close()
                os.remove(i)
                x.append(num)
                d =+ 1 
            except:
                print("-> Cannot unzip %s" % (i))
    for d in os.listdir(temp):
        if os.path.isdir(temp+"/"+d)==True:
            for j in os.listdir(temp+"/"+d):
                if j.endswith(".fz"):
                    os.system('funpack "%s/%s/%s"' % (temp, d, j))
                    os.system('rm "%s/%s/%s"' % (temp, d, j))
                    y.append(num)
    print("-> %d files unzipped and %d images funpacked\n" % (sum(x), sum(y)))

def movetar():
    '''
    moves data from /OASIS/temp to its respective target directory
    '''
    print("-> Moving data into target directories...")
    one = 1
    x = []
    temp = "%s/OASIS/temp" % (loc)
    for d in os.listdir(temp):
        files = glob.glob(temp + "/" + d + "/*.fits")
        for f in files:
            hdu = fits.open(f)
            tar = hdu[0].header['OBJECT']
            tar = tar.replace(' ', '_')
            data = "%s/OASIS/targets/%s" % (loc, tar)
            check = os.path.exists(data)
            if check == False:
                os.system("mkdir %s/OASIS/targets/%s" % (loc, tar))
            if f[-7] == "9":
                os.system("mv %s %s" % (f, data))
                x.append(one)
            if f[-7] == "0" or f[-7] == "1":
                os.remove(f)
        try:
            if os.listdir(temp + "/" + d) == []:
                os.rmdir(temp + "/" + d)
                print("-> removed %s because it became empty\n" % (d))
        except NotADirectoryError:
            pass
    print("-> moved %d images to %s\n" % (sum(x), data))
    if check == False:
        print("-> created %s directory in %s/OASIS/targets\n" % (tar, loc))

def rename():
    '''
    group images of same RA and DEC together in their own directories
    '''
    print("-> Grouping data by RA/DEC/Filter/ExposureTime...\n")
    x = []
    one = 1
    tars = []
    targets = loc + '/OASIS/targets'
    for d in os.listdir(targets):
        tars.append(d)
    for t in tars:
        target = targets + '/' + t
        length = len(target) + 1
        for f in glob.glob("%s/*.fits" % (target)):
            F = f[length:]
            hdu = fits.open(f, mode='update')
            ra = hdu[0].header['CAT-RA']
            dec = hdu[0].header['CAT-DEC']
            fltr = hdu[0].header['FILTER']
            exp = round(hdu[0].header['EXPTIME'])
            stoptime = hdu[0].header['UTSTOP']
            check = os.path.exists("%s/%s_%s" % (target, ra, dec))
            if check == False:
                os.system("mkdir %s/%s_%s" % (target, ra, dec))
                os.system("mkdir %s/%s_%s/%s" % (target, ra, dec, fltr))
                os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                if os.path.exists("%s/%s_%s/%s/%s/data/%s_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False and os.path.exists("%s/%s_%s/%s/%s/data/%s_ref_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False:
                    os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                    os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
                    data_loc =  "%s/%s_%s/%s/%s/data" % (target, ra, dec, fltr, exp)
                else:
                    os.remove(f)
            if check == True:
                check2 = os.path.exists("%s/%s_%s/%s" % (target, ra, dec, fltr))
                if check2 == False:
                    os.system("mkdir %s/%s_%s/%s" % (target, ra, dec, fltr))
                    os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                    create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                    if os.path.exists("%s/%s_%s/%s/%s/data/%s_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False and os.path.exists("%s/%s_%s/%s/%s/data/%s_ref_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False:
                        os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                        os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
                        data_loc =  "%s/%s_%s/%s/%s/data" % (target, ra, dec, fltr, exp)
                    else:
                        os.remove(f)
                if check2 == True:
                    check3 = os.path.exists("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                    if check3 == False:
                        os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                        create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                        if os.path.exists("%s/%s_%s/%s/%s/data/%s_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False and os.path.exists("%s/%s_%s/%s/%s/data/%s_ref_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False:
                            os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                            os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
                            data_loc =  "%s/%s_%s/%s/%s/data" % (target, ra, dec, fltr, exp)
                        else:
                            os.remove(f)
                    if check3 == True:
                        if os.path.exists("%s/%s_%s/%s/%s/data/%s_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False and os.path.exists("%s/%s_%s/%s/%s/data/%s_ref_A_.fits" % (target, ra, dec, fltr, exp, stoptime)) == False:
                            os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                            os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
                            data_loc =  "%s/%s_%s/%s/%s/data" % (target, ra, dec, fltr, exp)
                        else:
                            os.remove(f)
            x.append(one)
            (hdu[0].header).set('MASKED', 'N')
            hdu.close()
    print("-> %d images grouped into location directories\n" % (sum(x)))
    try:
        return data_loc
    except UnboundLocalError:
        pass
    