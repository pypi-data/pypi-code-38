# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:33:40 2019

@author: michaelek
"""




############################################
## Util functions

def where_gen(val, db_col, exist_dict=None):
    """

    """
    if val is None:
        where_dict = None
    elif isinstance(val, (str, int)):
        if isinstance(val, bool):
            if val:
                where_dict = {db_col: [1]}
            else:
                where_dict = {db_col: [0]}
        else:
            where_dict = {db_col: [val]}
    elif isinstance(val, list):
        if len(val) > 2000:
            where_dict = None
        else:
            where_dict = {db_col: val}
    else:
        raise ValueError('Input must be None, int, str, or a list')

    if exist_dict is not None:
        if where_dict is not None:
            new_dict = exist_dict.copy()
            new_dict.update(where_dict)
            return new_dict
        else:
            return exist_dict
    else:
        return where_dict

