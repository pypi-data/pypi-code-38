# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import sys
import json
import os
import logging
logger = logging.getLogger("seetaas-helper")

_api_host = "http://monitor-seetaas-backend-v1.seetaas.svc.cluster.local:8920/"


class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        super(DotDict, self).__init__()
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value

    def __delitem__(self, key):
        super(DotDict, self).__delitem__(key)
        del self.__dict__[key]

    # setstate and getstate is for pickle
    def __getstate__(self):
        pass

    def __setstate__(self, *args, **kwargs):
        pass


def _load_json(str):
    if sys.version_info.major >= 3:
        return json.loads(str)

    def json_loads_byteified(json_text):
        return _byteify(
            json.loads(json_text, object_hook=_byteify),
            ignore_dicts=True
        )

    def _byteify(data, ignore_dicts=False):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        if isinstance(data, list):
            return [_byteify(item, ignore_dicts=True) for item in data]
        if isinstance(data, dict) and not ignore_dicts:
            return {
                _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
            }
        return data

    return json_loads_byteified(str)


_parameter = None


def get_parameter():
    global _parameter
    if _parameter is not None:
        return _parameter
    parameter = os.getenv('AUTOCNN_PARAMETER', None)
    try:
        param = DotDict(_load_json(parameter)) if parameter else None
        _parameter = param
        return _parameter
    except Exception as e:
        logger.error('Could get parameters. {}'.format(e))
        return None


def write_parameter():
    argv = sys.argv
    if argv[1] == 'write' and len(argv) > 2:
        output_yml = argv[2]
    else:
        logger.error('Write Failed !!!\nUsage `helper write yml_file_name` to write parameters to yml')
        sys.exit(1)
    parameter = os.getenv('AUTOCNN_PARAMETER', None)
    try:
        if parameter is None:
            raise ValueError('Parameter is None')
        path = os.path.dirname(output_yml)
        if path and not os.path.isdir(path):
            os.makedirs(path)
        with open(output_yml, 'w') as fo:
            fo.write(parameter)
    except Exception as e:
        logger.error('Could get parameters. {}'.format(e))


def get_dataset_api():
    return os.getenv('AUTOCNN_DATASET_API', '').strip("/")


def get_metric_api():
    return os.getenv('AUTOCNN_METRIC_API', '').strip("/")


def get_data_attribute():
    info = os.getenv('AUTOCNN_DATA_ATTRIBUTE', None)
    try:
        return json.loads(info) if info else None
    except (ValueError, TypeError):
        logger.error('Could get dataset attribute info, '
                     'please make sure this is running inside a autodl job.')
        return None


def get_dataset_token():
    return os.getenv("AUTOCNN_DATASET_TOKEN", "")


def get_metric_token():
    return os.getenv("AUTOCNN_METRIC_TOKEN", "")


def get_output_dir():
    tgt = os.getenv("AUTOCNN_OUTPUT_PATH")
    out_num = int(os.getenv("AUTOCNN_OUTPUT_COUNT", "0"))
    if out_num <= 1:
        return tgt
    return [os.path.join(tgt, "%d" % i) for i in range(1, out_num+1)]


def get_input_dir():
    return os.getenv("AUTOCNN_INPUT_PATH")
