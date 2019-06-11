#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: violinsolo
# Created on 2019-06-10

# All fn utils for mapping ...

import numpy as np
# import pandas as pd
import json


def fn_map_ndarray_to_json(x):
    return json.dumps(np.asarray(x).tolist())


def fn_map_ndarray_to_json_faster(x):
    """
    not safe version of :function fn_map_ndarray_to_json
    :param x: pd.Series.item, type: np.ndarray.
    :return: json format string.
    """
    return json.dumps(x.tolist())


def fn_map_json_to_ndarray(x):
    if np.isnan(x):
        return x
    else:
        return np.asarray(json.loads(x))


def fn_map_json_to_ndarray_faster(x):
    return np.asarray(json.loads(x))
