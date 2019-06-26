#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 17:24:29 2018

@author: andrew
"""

import obtain
from initialize import loc
import data_request
import sys

def GET():
    '''Fetches and prepares data for difference imaging. Two ``get`` modes: 
    
        * *dl*: used to fetch images from the Las Cumbres Observatory (LCO) data archive.
        * *unpack*: used for non-LCO data. Users acquire images themselves and then call ``get`` in *unpack* mode to prepare the data for difference imaging.
    
    '''
    request_check = input("\n-> Get data from LCO or unpack downloaded data? (dl/unpack): ")
    if request_check == 'dl':
        data_request.request()
        obtain.move(loc+'/OASIS/temp')
        obtain.process()
        try:
            obtain.movetar()
        except UnboundLocalError:
            print("-> No data in 'temp' to move")
        obtain.rename()
    elif request_check == 'unpack':
        download_location = input("-> Enter LCO data location (leave blank for default=%s/Downloads): " % (loc))
        if download_location == "":
            download_location = "%s/Downloads" % (loc)
        obtain.move(download_location)
        obtain.process()
        try:
            obtain.movetar()
        except UnboundLocalError:
            print("-> No data in 'temp' to move")
        obtain.rename()
    else:
        print("-> Error: input must be 'dl' or 'unpack'")
        sys.exit()

if __name__ == '__main__':
    GET()