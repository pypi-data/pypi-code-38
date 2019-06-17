"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

#!/usr/bin/python2
"""Post status to monitor URL
>>> import ivi
>>> import new_u2000_client
>>> new_u2000_client.post_status("Testing")
result.reason= OK
result.status_code= 200
>>>
"""

import json
import requests
import time   # time is a module here
import multiprocessing
import sys
from os.path import join, dirname, abspath
# TODO: change instruments to a package to avoid this nonsense
sys.path.append(join(dirname(abspath(__file__)), "data_manipulation"))
from matlab_conversion import run_conversion_request
from configparser import ConfigParser
from gateway_helpers import get_headers

import settings

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']


def dt2ms(dtime):
    """Converts date time to miliseconds
    >>> from u2000_client import dt2ms
    >>> import datetime
    >>> dtime = datetime.datetime(2015, 12, 8, 18, 11, 44, 320012)
    >>> dt2ms(dtime)
    1449627104320
    """
    return int(dtime.strftime('%s'))*1000 + int(dtime.microsecond/1000)


def conversion_manager():
    while True:
        matlab_url = "https://" + settings.DOMAINNAME + "/gce_handler/Acme"
        response = authorize_and_request(matlab_url)
        ses = response[-1]
        response = response[0]
        print(response.text)
        if response.text:
            print("Checking for file")
            conversion_request = json.loads(response.text)
            run_conversion_request(ses, conversion_request)
        else:
            print("no conversion_request found in response")
        time.sleep(10)


def matlab_converter():
    """Process that converts data to matlab format"""
    ses = requests.session()
    while True:
        matlab_url = "https://" + \
            settings.DOMAINNAME + "/gce_handler/ubeam"
        response = authorize_and_request(matlab_url)
        if response:
            print("Checking for file")
            conversion_request = json.loads(response.text)
        if conversion_request:
            run_conversion_request(ses, conversion_request)
        else:
            print("no conversion_request found in response")
        time.sleep(10)


def request_commands():
    """polls the command URL for a start signal @ 10sec intervals"""
    command_url = "https://" + settings.DOMAINNAME + "/get_nuc_commands"
    response = authorize_and_request(command_url)
    return response.text


def authorize_and_request(url):
    headers = get_headers()
    ses = requests.session()
    response = ses.get(url, headers=headers)
    return response, ses


def command_manager(conversion_gets):
    try:
        command = "start_conversion_checks"
        if command == "start_conversion_checks":
            conversion_gets.start()
        elif command == "stop_conversion_checks":
            conversion_gets.terminate()
    except:
        print("command failed")
#        time.sleep(10)


if __name__ == "__main__":
    import os
    if not 'TEST_U2000_CLIENT' in os.environ:
        conversion_gets = multiprocessing.Process(target=conversion_manager)
        command_manager(conversion_gets)
    else:
        import doctest
        print("running doctest")
        doctest.testmod()
        print("doctest complete")


# To test, use "export TEST_U2000_CLIENT=1"
# To stop testing, "unset TEST_U2000_CLIENT"