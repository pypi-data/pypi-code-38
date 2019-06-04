# coding=utf-8
from __future__ import absolute_import, print_function

import math
import operator
from functools import reduce

import numpy as np


def toND(data, n):
    if len(data.shape) < n - 1:
        raise Exception("Data shape should more than {}D: {}".format(n - 1, data.shape))
    keeps = data.shape[1 - n :]
    layers = reduce(operator.mul, data.shape[: 1 - n], 1)
    return data.reshape((layers,) + keeps)


def to2D(data):
    return toND(data, 2)


def to3D(data):
    return toND(data, 3)


def to4D(data):
    return toND(data, 4)


def flatAsImage(data):
    data = to4D(data) if len(data.shape) > 3 and data.shape[-1] == 3 else to3D(data)
    layers, height, width = data.shape
    columnNumber = int(math.ceil(math.sqrt(layers)))
    rowNumber = layers // columnNumber + 1 if columnNumber > 1 else 1
    extraLayers = rowNumber * columnNumber - layers
    extraShape = (extraLayers, height, width)
    extraData = np.zeros(extraShape)
    fullData = np.concatenate([data, extraData])
    rows = [
        np.concatenate(fullData[i * columnNumber : (i + 1) * columnNumber], axis=1)
        for i in range(rowNumber)
    ]
    return np.concatenate(rows)
