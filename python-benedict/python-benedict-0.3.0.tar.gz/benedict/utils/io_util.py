# -*- coding: utf-8 -*-

import json
import requests
# import xmltodict
# import yaml


# def decode_base64(s):
#     return {}

def decode_json(s):
    return json.loads(s)
    # value = None
    # try:
    #     value = json.loads(s)
    # except Exception:
    #     pass
    # return value

# def decode_query_string(s):
#     return {}

# def decode_xml(s):
#     return {}

# def decode_yaml(s):
#     return {}

# def encode_base64(d):
#     return ''

def encode_json(d, *args, **kwargs):
    return json.dumps(d, *args, **kwargs)

# def encode_query_string(d):
#     return ''

# def encode_xml(d):
#     # https://pypi.org/project/dicttoxml/
#     return ''

# def encode_yaml(d):
#     return ''

def read_file(filepath):
    # try:
    handler = open(filepath, 'r')
    content = handler.read()
    handler.close()
    return content
    # except (OSError, IOError):
    #    return None

def read_url(url, *args, **kwargs):
    response = requests.get(url, *args, **kwargs)
    return response.text

def write_file(filepath, content):
    # try:
    handler = open(filepath, 'w+')
    handler.write(content)
    handler.close()
    return True
    # except (OSError, IOError):
    #    return False

