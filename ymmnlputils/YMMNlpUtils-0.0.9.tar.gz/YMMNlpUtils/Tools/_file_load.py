#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/25 10:23 AM
# @Author  : Slade
# @File    : _file_load.py

import pickle

def _writebunchobj(path, bunchobj):
    with open(path, "wb") as file_obj:
        pickle.dump(bunchobj, file_obj, 1)

def _readbunchobj(path):
    with open(path, "rb") as file_obj:
        bunch = pickle.load(file_obj)
    return bunch