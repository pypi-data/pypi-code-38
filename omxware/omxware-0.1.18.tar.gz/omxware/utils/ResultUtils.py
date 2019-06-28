# -*- coding: utf-8 -*-
"""
OMXWare Utils
"""

import pandas as pd


def list2str(dct):
    return_str = ''

    if isinstance(dct, list):
        i = 0;

        for x in dct:

            if i > 0:
                return_str = return_str + ','

            return_str = return_str + x
            i = i + 1

        return return_str


