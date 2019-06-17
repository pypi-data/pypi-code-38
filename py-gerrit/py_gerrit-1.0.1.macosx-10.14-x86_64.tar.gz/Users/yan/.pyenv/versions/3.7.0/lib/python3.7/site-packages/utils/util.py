# -*- coding: utf-8 -*-
# @Time    : 19-5-21 下午5:02
# @Author  : allen.you
import json
import logging

from config import GERRIT_MAGIC_JSON_PREFIX


def _decode_response(response):
    content = response.text.strip()
    response.raise_for_status()
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]
    try:
        return json.loads(content)
    except ValueError:
        logging.error('Invalid json content: %s' % content)
        raise


def decode_model(json_obj, object):
    all_objects = []

    for key, value in json_obj.items():
        # print(key, value)
        obj = object()
        obj.fromJson(value)
        all_objects.append(obj)

    return all_objects
