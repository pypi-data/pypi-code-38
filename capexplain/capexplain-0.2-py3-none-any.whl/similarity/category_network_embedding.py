#!/usr/bin/python
# -*- coding:utf-8 -*- 

import sys, getopt
import pandas
import csv
import numpy as np
import time
import math

from capexplain.utils import *


class CategoryNetworkEmbedding(object):
    """Summary of class here.
    """
    def __compute_cos_similarity(self, col, val1, val2):
        if col not in self.cate_cols:
            return -1
        else:
            # if 'vldb' in val1:
            #     val1 = 'vldb'
            # if 'vldb' in val2:
            #     val2 = 'vldb'
            if val1 not in self.vector_list or val2 not in self.vector_list:
                return -1
            list1 = self.vector_list[val1]
            list2 = self.vector_list[val2]
            
            res = 0.0
            len1 = 0.0
            len2 = 0.0
            for i in range(len(list1)):
                res = res + list1[i] * list2[i]
                len1 = len1 + list1[i] * list1[i]
                len2 = len2 + list2[i] * list2[i]
            return res / (math.sqrt(len1) * math.sqrt(len2))
            #return res

    def __init__(self, inf='', df=[], aggr_col='count'):
        """Inits SampleClass with blah."""
        
        self.vector_list = {}
        self.df = df
        self.cate_cols = {}

        if inf == '':
            return
        infile = open(inf, 'r')
        while True:
            line = infile.readline()
            if not line:
                break
            temp_arr = line.strip('\n\t').split(' ')
            self.vector_list[temp_arr[0]] = list(map(lambda x:float(x), temp_arr[1:]))

        for col in df:
            if col == 'index' or col == 'name':
                continue
            if df[col].dtype.kind == 'S' or df[col].dtype.kind == 'O':
                self.cate_cols[col] = True
        venue_list = ['conf/sigmod', 'conf/vldb', 'conf/icde', 'conf/pods', 'journals/pvldb','conf/icml','journals/vldb','conf/kdd','conf/aaai','conf/nips','conf/ijcai']
        for v1 in venue_list:
            for v2 in venue_list:
                print(v1, v2, self.__compute_cos_similarity('pubkey', v1, v2))

    def is_categorical(self, col):
        return col in self.cate_cols

    def compute_similarity(self, col, val1, val2, aggr_col):
        return (1.0 + self.__compute_cos_similarity(col, val1, val2)) * 0.5
