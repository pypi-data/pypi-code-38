#-*- coding:utf-8 -*-
"""
    core

    Copyright (c) 2018 Tetsuya Shinaji

    This software is released under the MIT License.

    http://opensource.org/licenses/mit-license.php
    
    Date: 2018/03/01

"""
import numpy as np
import copy
import traceback
from itertools import repeat
import re
from collections import OrderedDict
from logging import getLogger


class Dict(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        for key in self.keys():
            # new_key = re.sub("[^a-zA-Z0-9_]", "", key.replace(" ", "_"))
            # if str.isalpha(new_key[0]):
            #     if new_key == key or new_key not in self.keys():
            #         self.__dict__[new_key] = self[key]
            if isinstance(self[key], dict):
                self[key] = Dict(self[key])
        if "force_ndarray" in kwargs:
            if kwargs["force_ndarray"]:
                self.list_to_ndarray()

    def list_to_ndarray(self, keys: list=None, excludes: list=None):
        if keys is None:
            keys = self.keys()
        if excludes is None:
            excludes = []
        for key in keys:
            if key in excludes or key not in self.keys():
                continue
            if isinstance(self[key], list):
                self[key] = np.array(self[key])

    def ndarray_to_list(self, keys: list = None, excludes: list = None):
        if keys is None:
            keys = self.keys()
        if excludes is None:
            excludes = []
        for key in keys:
            if key in excludes or key not in self.keys():
                continue
            if isinstance(self[key], np.ndarray):
                self[key] = self[key].tolist()

    def where(self, child_key, op: str, value):
        """
        filter dict based on child value
        :param child_key: target child key
        :param op: operator (supporting "==", ">=", "<=", ">", "<", "!=")
        :param value: value
        :return: filtered dict
        """
        if op not in ["==", ">=", "<=", "!=", "<", ">"]:
            raise KeyError(f"Unknown operator was given. {op}")
        if op == "==":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] == value)
                }
            )
        elif op == ">":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] > value)
                }
            )
        elif op == "<":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] < value)
                }
            )
        elif op == ">=":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] >= value)
                }
            )
        elif op == "<=":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] <= value)
                }
            )
        elif op == "!=":
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        self[key][child_key] != value)
                }
            )

    def __str__(self):
        ret = ""
        for key in self.keys():
            if isinstance(self[key], str):
                ret += f'"{key}": "{self[key]}", '
            else:
                ret += f'"{key}": {self[key]}, '
        return ("{" + ret[:-2] + "}").replace("'", '"')

    def __mul__(self, other: int):
        if isinstance(other, int):
            return repeat(copy.deepcopy(self), other)
        else:
            raise TypeError

    def __add__(self, other: [dict, 'Dict']):
        new_dict = copy.deepcopy(self)
        new_dict += other
        return new_dict

    def __radd__(self, other: [dict, 'Dict']):
        if other == 0 and isinstance(other, int):
            return copy.deepcopy(self)
        elif isinstance(other, dict):
            return self + Dict(other)
        elif isinstance(other, Dict):
            return self + other
        else:
            raise TypeError

    def __iadd__(self, other: [dict, 'Dict']):

        logger = getLogger(__name__)
        if isinstance(other, (dict, Dict)):
            for key in other.keys():
                if key in self.keys():
                    try:
                        if isinstance(self[key], list):
                            if isinstance(other[key], list):
                                self[key] += other[key]
                            else:
                                self[key].append(other[key])
                        elif isinstance(self[key], np.ndarray):
                            logger.debug(
                                "Cannot keep numpy array. "
                                f"Numpy array of key='{key}' was converted to list.")
                            self[key] = self[key].tolist()
                            if isinstance(other[key], list):
                                self[key] += other[key]
                            elif isinstance(other[key], np.ndarray):
                                self[key] += other[key].tolist()
                            else:
                                self[key] += [other[key]]
                        elif isinstance(other[key], (dict, Dict)):
                            if isinstance(self[key], (dict, Dict)):
                                self[key] = Dict(self[key]) + Dict(other[key])
                            else:
                                self[key] = [self[key], other[key]]
                        else:
                            self[key] = [self[key], other[key]]
                    except:
                        logger.debug(traceback.format_exc())
                else:
                    self.update(Dict({key: other[key]}))
        else:
            raise TypeError

        return self

