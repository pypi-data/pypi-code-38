#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import os
import make_stars
import glob
import sys

def initialize(loc):
    '''
    run on a new computer to create the OASIS file system and use the pipeline
    '''
    if os.path.exists(loc + "/OASIS") == False:
        os.system("mkdir %s/OASIS" % (loc))
        os.system("mkdir %s/OASIS/targets" % (loc))
        os.system("mkdir %s/OASIS/temp" % (loc))
        os.system("mkdir %s/OASIS/archive" % (loc))
        os.system("mkdir %s/OASIS/config" % (loc))
        os.system("mkdir %s/OASIS/simulations" % (loc))
        os.system("mkdir %s/OASIS/archive/data" % (loc))
        os.system("mkdir %s/OASIS/archive/templates" % (loc))
        os.system("mkdir %s/OASIS/archive/residuals" % (loc))
        os.system("cp %s/config/OASIS.config %s/OASIS/config" % (os.path.dirname(make_stars.__file__), loc))
        print("-> OASIS file system created in %s\n" % (loc))
    else:
        print("-> OASIS architecure already exists on this computer")

def create(location):
    '''
    creates a data, template, and residual directory
    '''
    dirs = ["data", "templates", "residuals", "sources", "psf"]
    for d in dirs: 
        if os.path.exists("%s/%s" % (location, d)) == False:
            os.system("mkdir %s/%s" % (location, d))
            print("-> %s directory created in %s\n" % (d, location))

def create_configs(location):
    check_configs = location + '/configs'
    if os.path.exists(check_configs) == False:
        os.mkdir(check_configs)
    config_loc = os.path.dirname(make_stars.__file__) + '/config'
    for files in glob.glob(config_loc + '/*'):
        os.system('cp -n %s %s' % (files, check_configs))
        
def get_loc():
    config_loc = os.path.dirname(make_stars.__file__) + '/config/OASIS.config'
    with open(config_loc, 'r') as conf:
        lines = conf.readlines()
    for l in lines:
        if l.split()[0] == 'loc':
            return l.split()[1]
            break

def get_config_value(keyword, config_file='OASIS.config'):
    config_loc = get_loc() + '/OASIS/config'
    with open("%s/%s" % (config_loc, config_file), 'r') as conf:
        lines = conf.readlines()
    for l in lines:
        if l.split()[0] == keyword:
            value = l.split()[1]
            try: value = float(value)
            except: pass
            return value
            break
        
#get OASIS file tree location from OASIS.config file
loc = get_loc()

def INITIALIZE():
    '''
    Sets up the **OASIS** environment on a new machine. Creates the **OASIS** file tree and installs Alard's ``ISIS`` program (see documentation for details).
    '''
    alert = input("-> Build OASIS file tree in %s? (y/n): " % (loc))
    if alert == 'y':
        initialize(loc)
    elif alert == 'n':
        print("-> Change loc variable in initialize.py to desired OASIS directory path, then run script again")
        sys.exit()
    else:
        print("-> Error: unknown input")
        sys.exit()
    ais_install = input("-> Install ISIS image subtraction software on this machine (requires C shell)? (y/n): ")
    if ais_install == 'y':
        ais_run = os.path.dirname(make_stars.__file__) + '/AIS/package/./install.csh'
        os.system(ais_run)
    elif ais_install == 'n':
        pass
    else:
        print("-> Error: unknown input")
        sys.exit()
        
#if this architecture does not exist, create it
if __name__ == '__main__':
    INITIALIZE()