import hashlib
import re
import os
import sys
import platform
from collections import OrderedDict

from requests import get, Session


def ip42pl():
    return get('http://ip.42.pl/raw').text


def jsonip():
    return get('http://jsonip.com').json()['ip']


def httpbin():
    return get('http://httpbin.org/ip').json()['origin'].split(',')[0]


def ipify():
    return get('https://api.ipify.org/?format=json').json()['ip']


def get_public_ip():
    for f in [httpbin, ip42pl, jsonip, ipify]:
        try:
            ret = f()
        except Exception as e:
            pass
        else:
            return ret


def hexMD5(value):
    h = hashlib.md5()
    h.update(value.encode())
    return h.hexdigest()


def read_keyword_file(_file):
    if not _file:
        return
    with open(_file) as fp:
        keyword_list = fp.readlines()
        keyword_list = list(map(str.strip, keyword_list))
        return keyword_list


def _float2str(float_val):
    try:
        val = str(int(float_val))
    except Exception as e:
        return float_val
    else:
        return val
