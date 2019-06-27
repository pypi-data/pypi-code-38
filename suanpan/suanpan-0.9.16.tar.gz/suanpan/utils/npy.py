# coding=utf-8
from __future__ import absolute_import, print_function

import numpy as np

from suanpan.utils import json


def loadjson(obj, *args, **kwargs):  # pylint: disable=unused-argument
    return np.frombuffer(obj["data"], obj["dtype"]).reshape(obj["shape"])


def loadjsons(s, *args, **kwargs):
    obj = json.loads(s, *args, **kwargs)
    obj["data"] = obj["data"].encode()
    return loadjson(obj)


def loadjsonf(file, *args, **kwargs):
    obj = json.load(file, *args, **kwargs)
    obj["data"] = obj["data"].encode()
    return loadjson(obj)


def dumpjson(npy, *args, **kwargs):  # pylint: disable=unused-argument
    return {"dtype": str(npy.dtype), "shape": npy.shape, "data": npy.tobytes()}


def dumpjsons(npy, *args, **kwargs):
    obj = dumpjson(npy)
    obj["data"] = obj["data"].decode()
    return json.dumps(obj, *args, **kwargs)


def dumpjsonf(npy, fp, *args, **kwargs):
    obj = dumpjson(npy)
    obj["data"] = obj["data"].decode()
    return json.dump(obj, fp, *args, **kwargs)


def load(file, *args, **kwargs):
    return np.load(file, *args, **kwargs)


def dump(npy, file, *args, **kwargs):
    return np.save(file, npy, *args, **kwargs)
