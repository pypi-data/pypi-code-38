#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import ast
import base
import collections
import datetime
import json
import os
import re
import requests
import settings
import subprocess
import usb
from math import log10
from threading import Thread
import functools
import time
from base import t_diagnostic_logger as tlogger


os.environ['NO_PROXY'] = 'gradientone.com'
os.environ['no_proxy'] = 'gradientone.com'

COMPANYNAME = settings.COMPANYNAME
COMMON_SETTINGS = settings.COMMON_SETTINGS
CLIENT_SETTINGS = settings.CLIENT_SETTINGS
TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL
logger = base.get_logger()


def set_pid_json_file(json_file='', counter=0):
    counter += 1
    max_tries = 10
    if not json_file:
        json_file = os.path.join(TMPDIR, 'pids.json')
    if counter > max_tries:
        logger.warning("exceeded max tries setting json file...")
        logger.warning("simply using " + json_file)
        return json_file
    if os.path.isfile(json_file):
        try:
            with open(json_file, 'r') as f:
                f.read()
            return json_file
        except Exception as e:
            logger.info("Exception reading pid json file: ".format(e))
            logger.info("setting new pid json file")
            json_file = json_file + '.' + str(counter)
            return set_pid_json_file(json_file=json_file, counter=counter)


PID_JSON_FILE = set_pid_json_file()


def authorize_and_post(session, url, data):
    headers = base.get_headers()
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 401:
        headers = base.get_headers(refresh=True)
        response = session.post(url, headers=headers, data=data)
    return response


def dt2ms(dtime):
    """Converts date time to miliseconds
    >>> from u2000_client import dt2ms
    >>> import datetime
    >>> dtime = datetime.datetime(2015, 12, 8, 18, 11, 44, 320012)
    >>> dt2ms(dtime)
    1449627104320
    """
    delta = dtime - datetime.datetime(1970, 1, 1)
    return int(delta.total_seconds()) * 1000 + int(delta.microseconds / 1000)


def post_log(message, session=None):
    """posts logs to the server for info and troubleshooting"""
    return
    # Commented out because log posts are timing out
    # logger.info("posting log message: %s" % message)
    # if not session:
    #     session = requests.session()
    # headers = {'Content-Type': 'text/plain', 'Accept': 'text/plain'}
    # data = {
    #     'message': message,
    #     'time': datetime.datetime.now().isoformat(),
    # }
    # json_data = json.dumps(data, ensure_ascii=True)
    # url_s = (BASE_URL + "/nuc_logs/" +
    #          COMMON_SETTINGS['COMPANYNAME'] + '/' +
    #          settings.GATEWAY_ID)
    # response = session.post(url_s, data=json_data, headers=headers)
    # logger.info("post_log response: %s" % response)


def round_dec(val, decimal_place=3):
    """Rounds to a given decimal place and rounds up on 5
       >>> round_dec(0.0045)
       0.005
       >>> round_dec(4.5e-05)
       0.0
       >>> round_dec(4.5e-05, 5)
       5e-05
       """
    val += 0.01 * 10 ** -decimal_place
    rounded_val = round(val, decimal_place)
    if rounded_val > 1e+36:
        rounded_val = float(str(rounded_val))
    return rounded_val


def round_sig(val, digits=3):
    """Rounds value to specified significant digits by determining
       decimal place needed to round number value and calling round_dec
       >>> round_sig(6.3193e-9)
       6.32e-09
       >>> round_sig(6.3193e-9, 4)
       6.319e-09
       >>> round_sig(0.55550)
       0.556
       """
    if val == 0:
        return 0.0
    decimal_place = int(-log10(abs(val))) + digits
    return round_dec(val, decimal_place)


def safe_json_loads(eval_str, default=collections.defaultdict(int)):
    try:
        retval = json.loads(eval_str)
    except Exception:
        retval = legacy_ast(eval_str, default)
    return retval


def legacy_ast(eval_str, default=collections.defaultdict(int)):
    try:
        retval = ast.literal_eval(eval_str)
    except Exception:
        retval = default
    return retval


def reset_device_with_tag(tag='Tektronix'):
    if not tag:
        tag = 'Tektronix'
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+)." +
                           "+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    # collect all the device information into a list of devices
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                path_to_device = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'),
                                                         dinfo.pop('device'))
                dinfo['path_to_device'] = path_to_device
                devices.append(dinfo)
    path_to_device = None
    # check the list of devices against the 'tag'
    for d in devices:
        if tag in d['tag']:
            path_to_device = d['path_to_device']
            break
    # if no path found, use the default
    if not path_to_device:
        path_to_device = '/dev/bus/usb/002/003'
    folder = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(folder, 'usbreset')
    e = file_path + ' ' + path_to_device
    subprocess.call(e, shell=True)


def authorize_and_request(url):
    headers = base.get_headers()
    ses = requests.session()
    response = ses.get(url, headers=headers)
    return response, ses


def decimation_factor(record_length):
    """Returns decimation factor based on record length"""
    dec_factors = {100000: 10, 125000: 12, 1000000: 100,
                   1250000: 125, 5000000: 500, 10000000: 1000, 20000000: 2000}
    factor = dec_factors[record_length]
    return factor


def authorize_and_get(url):
    """Authorizes request to url and makes GET"""
    headers = base.get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        headers = base.get_headers(refresh=True)
        response = requests.get(url, headers=headers)
    return response


def get_pid_list():
    if not PID_JSON_FILE:
        return []
    pid_list = []
    try:
        if not os.path.isfile(PID_JSON_FILE):
            with open(PID_JSON_FILE, 'w') as f:
                f.write(json.dumps(pid_list))
        with open(PID_JSON_FILE, 'r') as f:
            data = f.read()
            if data:
                pid_list = json.loads(data)
    except IOError as e:
        # not able to read the file
        logger.warning("IOError get_pid_list(): {}".format(e))
    except TypeError as e:
        # bad data in the file
        logger.warning("TypeError get_pid_list(): {}".format(e))
    except Exception as e:
        logger.error("Unexpected error in get_pid_list(): {}".format(e))

    return pid_list


def save_pid(pid):
    if not PID_JSON_FILE:
        return None
    pid_list = get_pid_list()
    pid_list.append(pid)
    try:
        with open(PID_JSON_FILE, 'w') as f:
            f.write(json.dumps(pid_list))
    except IOError as e:
        # not able to read the file
        logger.warning("IOError save_pid(): {}".format(e))
    except TypeError as e:
        # bad data in the file
        logger.warning("TypeError save_pid(): {}".format(e))
    except Exception as e:
        logger.error("Unexpected error in save_pid(): {}".format(e))


def clear_pid_list():
    if not PID_JSON_FILE:
        return None
    pid_list = []
    try:
        with open(PID_JSON_FILE, 'w') as f:
            f.write(json.dumps(pid_list))
    except IOError as e:
        # not able to read the file
        logger.warning("IOError clear_pid_list(): {}".format(e))
    except TypeError as e:
        # bad data in the file
        logger.warning("TypeError clear_pid_list(): {}".format(e))
    except Exception as e:
        logger.error("Unexpected error in clear_pid_list(): {}".format(e))


class TimeoutError(Exception):
    def __init__(self, *args):
        super(TimeoutError, self).__init__('Timeout',*args)


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            origResult = TimeoutError(
                         'function [%s] timeout [%s seconds] exceeded!' % (
                                                     func.__name__, timeout))
            res = [origResult]
            def newFunc():
                try:
                    result = func(*args, **kwargs)
                except Exception, e:
                    result = e
                res[0] = result
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception, je:
                print 'error starting thread'
                raise je
            result = res[0]  # get result from thread
            if isinstance(result, BaseException):
                tlogger.error('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))
                raise result
            return result
        return wrapper
    return deco

