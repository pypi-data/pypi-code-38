# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

import sys
import hmac
import hashlib

from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qsl

from tcell_agent.config.configuration import get_config


USE_PYTHON_2_HASH = (sys.version_info.major == 2 and hash("hash") == 7799588877615763652)


def java_hash(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def python_dependent_hash(s):
    if USE_PYTHON_2_HASH:
        return hash(s)

    return java_hash(s)


def tcell_hmac(value):
    config = get_config()
    hmac_key = config.hmac_key or config.app_id

    try:
        hmac_key_enc = bytes(hmac_key, "utf-8")
    except Exception:
        hmac_key_enc = bytes(hmac_key)
    digest = hmac.new(hmac_key_enc, str(value).encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def hmac_half(value):
    hmacd = tcell_hmac(value)
    if hmacd and len(hmacd) > 32:
        hmacd = hmacd[0:32]
    return hmacd


def strip_query_string(query_string):
    query_string_type = str(type(query_string))

    # use utf-8 decoding to change it to unicode in python2
    if query_string_type.startswith("<type 'str'"):
        query_string = query_string.decode("utf-8")

    query_params = parse_qsl(query_string, keep_blank_values=True)
    return urlencode([(param_name, "",) for param_name, _ in query_params])


def strip_uri(uri):
    scheme, netloc, path, query_string, fragment = urlsplit(uri)
    query_string = strip_query_string(query_string)
    if fragment is not None and fragment != "":
        fragment = tcell_hmac(fragment)

    return urlunsplit((str(scheme), str(netloc), str(path), str(query_string), str(fragment)))
