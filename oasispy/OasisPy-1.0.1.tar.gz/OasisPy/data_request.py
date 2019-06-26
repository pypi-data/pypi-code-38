#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 14:20:26 2018

@author: Nestor Espinoza
"""

import os
import time
import calendar
import requests
import numpy as np
import proposals
from initialize import loc
import sys

def download_frames(sdate, edate, headers, prop, datafolder):
    """Download files
      This function downloads all the frames for a given range of dates, querying
      50 frames at a time (i.e., if 150 frames have to be downloaded, the process 
      is repeated 3 times, each time downloading 50 frames). This number 
      assumes connections can be as bad as to be able to download only ~1 Mb per 
      minute (each get request shares file urls that last 48 hours only), assuming 
      60 MB frames (worst case scenarios).
 
      It returns the number of total identified frames for the given range and the 
      number of frames downloaded (which is equal to the number of identified frames 
      if no data for that time range was detected on the system).
      Args:
          sdate (time.time): Search for data collected on this date or later
          edate (time.time): Search for data collected before this date
          headers (dict): authentication token from the LCO archive
          prop (list): List of proposal IDs to search for
          datafolder (string): Directory to put the data
      Returns:
          tuple: list of files found on the archive, list of files actually downloaded
    """
    nidentified = 0
    ndownloaded = 0
    response = requests.get('https://archive-api.lco.global/frames/?' +
                            'limit=50&' +
                            'RLEVEL=91&' +
                            'start='+sdate+'&' +
                            'end='+edate+'&' + 
                            'PROPID='+prop+'&',
#                            'OBJECT='+obj+'&', 
#                            'SITEID='+siteid+'&' + 
#                            'TELID='+telid+'&' + 
#                            'Filter='+fltr+'&',
#                            'EXPTIME='+exptime+'&',
                            headers=headers).json()

    frames = response['results']
    if len(frames) != 0:
        print('\t-> Frames identified for the '+sdate+'/'+edate+' period. Checking frames...')
        while True:
            for frame in frames:
                nidentified += 1
                # Get date of current image frame:
                date = frame['filename'].split('-')[2]

                # Create new folder with the date if not already there:
                outpath = os.path.join(datafolder, date)
                if not os.path.exists(outpath):
                    os.mkdir(outpath)

                # Check if file is already on disk and that is not a _cat.fits. If not there
                # and is not a _cat.fits, download the file:
                if not os.path.exists(os.path.join(outpath, frame['filename'])) and\
                   '_cat.fits' != frame['filename'][-9:]:
                    print('->   + File '+frame['filename']+' not found in '+outpath)
                    print('->     Downloading ...')
                    with open(os.path.join(outpath, frame['filename']), 'wb') as f:
                        f.write(requests.get(frame['url']).content)
                    ndownloaded += 1
            if response.get('next'):
                response = requests.get(response['next'], headers=headers).json()
                frames = response['results']
            else:
                break
    return nidentified, ndownloaded

def get_headers_from_token(username, password):
    """
      This function gets an authentication token from the LCO archive.
      Args:
          username (string): User name for LCO archive
          password (string): Password for LCO archive
      Returns:
          dict: LCO authentication token
    """
    # Get LCOGT token:
    response = requests.post('https://archive-api.lco.global/api-token-auth/',
                             data={'username': username,
                                   'password': password}
                             ).json()

    token = response.get('token')

    # Store the Authorization header
    headers = {'Authorization': 'Token ' + token}
    return headers

def request():
    # Get data from user file:
    username = str(input("-> Enter LCO username: "))
    password = str(input("-> Enter LCO password: "))
    props = proposals.get_proposals(username, password)
    if props != []:
        print("\n-> Your proposals:\n")
        for i in props:
            print("\t " + i + "\n")
    else:
        print("-> No proposals attached to your account\n")
        sys.exit()
    proposal = str(input("-> Enter proposal you wish to download data from: "))
    datafolder = str(input("-> Enter destination of downloaded files (defaut=%s): " % (loc+"/OASIS/temp")))
    if datafolder == "":
        datafolder = loc + "/OASIS/temp"
    starting_date = str(input("-> Enter starting date [YYYY-MM-DD] (default=2017-01-01): "))
    if starting_date == "":
        starting_date = '2017-01-01'
    ending_date = str(input("-> Enter ending date [YYYY-MM-DD] (default= today's date): "))
    if ending_date == "":
        ending_date = time.strftime("%Y-%m-%d")
        c_y, c_m, c_d = ending_date.split('-')
        if int(c_d) + 1 <= calendar.monthrange(int(c_y), int(c_m))[-1]:
            ending_date = c_y + '-' + c_m + '-' + str(int(c_d) + 1)
        elif int(c_m) + 1 <= 12:
            ending_date = c_y + '-' + str(int(c_m) + 1) + '-01'
        else:
            ending_date = str(int(c_y) + 1) + '-01-01'
    headers = get_headers_from_token(username, password)

    # Get frame names from starting to ending date:
    c_y, c_m, c_d = starting_date.split('-')
    e_y, e_m, e_d = np.array(ending_date.split('-')).astype('int')
    while True:
        sdate = c_y + '-' + c_m + '-' + c_d
        if int(c_d) + 1 <= calendar.monthrange(int(c_y), int(c_m))[-1]:
            edate = c_y + '-' + c_m + '-' + str(int(c_d) + 1)
        elif int(c_m) + 1 <= 12:
            edate = c_y + '-' + str(int(c_m) + 1) + '-01'
        else:
            edate = str(int(c_y) + 1) + '-01-01'

        # Download frames in the defined time ranges:
        nidentified, ndownloaded = download_frames(sdate, edate, headers, proposal, datafolder)
        if nidentified != 0:
            print('-> Final count: ' + str(nidentified) + ' identified frames, downloaded ' +
                  str(ndownloaded) + ' new ones.')

        # Get next year, month and day to look for. If it matches the user-defined
        # or current date, then we are done:
        c_y, c_m, c_d = edate.split('-')
        if int(c_y) == e_y and int(c_m) == e_m and int(c_d) == e_d:
            break

    print('\n-> Done!\n')