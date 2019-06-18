# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import copy

import numpy as np


class CachedMethod(object):
    """

    """
    def __init__(self):
        self.cache = []

    def __call__(self, func):
        """

        :param func:
        :type func:
        :return:
        :rtype:
        """

        def method_wrapper(*args, **kwargs):
            """

            :param args:
            :type args:
            :param kwargs:
            :type kwargs:
            :return:
            :rtype:
            """

            hashes = CachedMethod._get_hashes(args + tuple(kwargs.values()))
            hash_value = hash(hashes)

            cache_result = [
                item[1]
                for item in self.cache
                if item[0] == hash_value
            ]
            if cache_result:
                return copy.deepcopy(cache_result[0])

            result = func(*args, **kwargs)
            if len(self.cache) > 10:
                del self.cache[0]
            self.cache.append((hash_value, copy.deepcopy(result)))

            return result

        return method_wrapper

    @staticmethod
    def _get_hashes(args):
        """

        :param arg:
        :type arg:
        :return:
        :rtype:
        """
        hashes = ()
        for arg in args:
            if isinstance(arg, np.ndarray):
                trans_arg = arg.tostring()
                hashes += (hash(trans_arg), )
            elif isinstance(arg, tuple):
                hashes += CachedMethod._get_hashes(arg)
            else:
                trans_arg = arg
                hashes += (hash(trans_arg), )
        return hashes
