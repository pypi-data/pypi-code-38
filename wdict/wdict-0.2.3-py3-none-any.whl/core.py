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
import sys
from collections.abc import Iterable
from itertools import chain


class Dict(OrderedDict):

    def __init__(self, *args, **kwargs):
        """
        init
        """
        super(Dict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        for key in self.keys():
            # new_key = re.sub("[^a-zA-Z0-9_]", "", key.replace(" ", "_"))
            # if str.isalpha(new_key[0]):
            #     if new_key == key or new_key not in self.keys():
            #         self.__dict__[new_key] = self[key]
            if isinstance(self[key], dict):
                self[key] = Dict(self[key])
        # convert list to ndarray
        if "force_ndarray" in kwargs:
            if kwargs["force_ndarray"]:
                self.list_to_ndarray()

    @staticmethod
    def __check_n_recursion(n: int):
        """
        check if number of recursion is less than n
        :param n: number of planned recursion
        :return:
        """
        if n >= sys.getrecursionlimit() - 1:
            raise RecursionError(
                f"To process this action, "
                f"you need {n} times recursion \n"
                f"But the system recursion limit is "
                f"{sys.getrecursionlimit() - 1}..."
            )

    def list_to_ndarray(self, keys: list=None, excludes: list=None):
        """
        convert list to ndarray
        :param keys: target keys, apply to all list elements in default
        :param excludes: excluding keys
        :return:
        """
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
        """
        convert ndarray element to list
        :param keys: target keys, apply to all ndarray elements in default
        :param excludes: excluding keys
        :return:
        """
        if keys is None:
            keys = self.keys()
        if excludes is None:
            excludes = []
        for key in keys:
            if key in excludes or key not in self.keys():
                continue
            if isinstance(self[key], np.ndarray):
                self[key] = self[key].tolist()

    def exclude(self, ignores):
        """
        exclude given keys
        :param ignores: ignores
        :return: Dict
        """
        return Dict({
            key: self[key] for key in self.keys() if key not in ignores
        })

    def extract(self, target_keys):
        """
        exclude keys which are not included in target keys
        :param target_keys: target keys
        :return: Dict
        """
        return Dict({
            key: self[key] for key in self.keys() if key in target_keys
        })

    def extract_child(self, child_key):
        """
        remove unnecessary children
        :param child_key: rule of extraction
        :return: new Dict
        """
        tmp = self.has_child(child_key)
        if "/" not in child_key:
            if child_key == "*":
                return Dict(self)
            else:
                ret = Dict({
                    key: Dict(tmp[key]).extract([child_key])
                    for key in tmp.keys()
                    if (hasattr(tmp[key], "keys"))
                })
        else:
            depth = child_key.split("/")
            self.__check_n_recursion(len(depth))
            ret = Dict({
                key: Dict(tmp[key]).extract_child("/".join(depth[1::]))
                for key in tmp.keys()
                if hasattr(tmp[key], "keys")
            })

        return ret.has_child(child_key)

    def has_child(self, child_key):
        """
        exclude elements which does not have the given child key
        :param child_key:
        :return:
        """
        if "/" not in child_key:
            if child_key == "*":
                return self
            else:
                return Dict({
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys())
                })

        else:
            depth = child_key.split("/")
            self.__check_n_recursion(len(depth))
            return Dict({
                key: self[key] for key in self.keys()
                if (hasattr(self[key], "keys") and
                    (depth[0] == "*" or depth[0] in self[key].keys()) and
                    len(Dict(self[key]).has_child(
                        "/".join(depth[1::])).keys()) > 0
                    )
            })

    @staticmethod
    def __drop_depth_0_keys(target_dict):
        """
        remove depth 0 keys
        :param target_dict:
        :return:
        """
        ret = [
            Dict(target_dict[key])
            for key in target_dict.keys()
            if hasattr(target_dict[key], "keys")]
        return sum(ret)

    def drop(self, depth: int):
        """
        drop target depth
        :param depth: target depth
        :return: Dict
        """
        if depth == 0:
            return self.__drop_depth_0_keys(self)
        self.__check_n_recursion(depth)
        new_dict = {}
        for key in self.keys():
            new_dict.update({key: Dict(self[key]).drop(depth-1)})
        return Dict(new_dict)

    def get_child_keys(self, path: str = None):
        """
        return unique keys of target path
        :param path: path to target depth
        :return: list
        """

        if path is None or path == "":
            return list(set(chain.from_iterable(
                [self[key].keys()
                 for key in self.keys()
                 if hasattr(self[key], "keys")]
            )))

        tmp = self.has_child(path)
        if len(tmp.keys()) == 0:
            return []
        depth = path.split("/")
        if len(depth) == 1:
            return list(set(chain.from_iterable([
                tmp[key][depth[0]].keys() for key in tmp.keys()
                if hasattr(tmp[key][depth[0]], "keys")
            ])))
        self.__check_n_recursion(len(depth))
        return tmp.drop(0).get_child_keys("/".join(depth[1::]))


    @staticmethod
    def __where_in_helper(child_value, given_value):
        try:
            return child_value in given_value
        except TypeError:
            return False

    @staticmethod
    def __where_not_in_helper(child_value, given_value):
        try:
            return child_value not in given_value
        except TypeError:
            return True

    @staticmethod
    def __where_has_helper(child_value, given_value):
        try:
            return isinstance(child_value, Iterable) and \
                   given_value in child_value
        except TypeError:
            return False

    @staticmethod
    def __where_does_not_have_helper(child_value, given_value):
        try:
            if not isinstance(child_value, Iterable):
                True
            return given_value not in child_value
        except TypeError:
            return True

    def where(self, child_key, op: str, value):
        """
        filter dict based on child value
        :param child_key: target child key
        :param op: operator (supporting "==", ">=", "<=", ">", "<", "!=",
                             "in", "not in", "has", "not has")
        :param value: value
        :return: filtered dict
        """
        if op not in ["==", ">=", "<=", "!=", "<", ">",
                      "in", "not in", "has", "does not have"]:
            raise KeyError(f"Unknown operator was given. {op}")

        if op == "==":
            comp_func = lambda child_value, given_value: child_value == given_value
        elif op == ">":
            comp_func = lambda child_value, given_value: child_value > given_value
        elif op == "<":
            comp_func = lambda child_value, given_value: child_value < given_value
        elif op == ">=":
            comp_func = lambda child_value, given_value: child_value >= given_value
        elif op == "<=":
            comp_func = lambda child_value, given_value: child_value <= given_value
        elif op == "!=":
            comp_func = lambda child_value, given_value: child_value != given_value
        elif op == "in":
            if not isinstance(value, Iterable):
                raise ValueError(f"value ({value}) must be iterable")
            comp_func = self.__where_in_helper
        elif op == "not in":
            if not isinstance(value, Iterable):
                raise ValueError(f"value ({value}) must be iterable")
            comp_func = self.__where_not_in_helper
        elif op == "has":
            comp_func = self.__where_has_helper
        elif op == "does not have":
            comp_func = self.__where_does_not_have_helper

        if "/" not in child_key:
            if child_key == "*":
                raise ValueError(
                    f"Cannot use wildcard at end of child_key\n"
                    f"given child_key was {child_key}"
                )
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        child_key in self[key].keys() and
                        comp_func(self[key][child_key], value)
                        )
                }
            )
        else:
            depth = child_key.split("/")
            self.__check_n_recursion(len(depth))
            return Dict(
                {
                    key: self[key] for key in self.keys()
                    if (hasattr(self[key], "keys") and
                        (depth[0] == "*" or depth[0] in self[key].keys()) and
                        len(Dict(self[key]).where(
                            "/".join(depth[1::]), op, value).keys()) > 0
                        )
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

