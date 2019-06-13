#!/usr/bin/python
# -*- coding:utf-8 -*- 

import sys, getopt
import pandas
import csv
import time
import math

from capexplain.utils import *

def compare(t1, t2, aggr_col):
    for k in range(0, len(t1)):
        if t1[k] != t2[k]:
            if t1[k] < t2[k]:
                return -1
            else:
                return 1
    return 0

class CategoryEmbedding(object):
    """Summary of class here.
    """

    def __compute_distance(self, col, val1, val2, aggr_col):
        if col not in self.cate_cols:
            return -1
        else:
            if val1 not in self.cate_cols[col] or val2 not in self.cate_cols[col]:
                return -1
            len1 = len(self.cate_cols[col][val1])
            len2 = len(self.cate_cols[col][val2])
            i = 0
            j = 0
            dist = 0.0
            cnt = 0
            while i < len1 and j < len2:
                cmp_res = compare(self.cate_cols[col][val1][i][0], self.cate_cols[col][val2][j][0], aggr_col)
                cnt += 1
                if cmp_res == 0:
                    dist += (self.cate_cols[col][val1][i][1] - self.cate_cols[col][val2][j][1]) * (self.cate_cols[col][val1][i][1] - self.cate_cols[col][val2][j][1])
                    i += 1
                    j += 1
                elif cmp_res < 0:
                    dist += self.cate_cols[col][val1][i][1] * self.cate_cols[col][val1][i][1]
                    i += 1
                else:
                    dist += self.cate_cols[col][val2][j][1] * self.cate_cols[col][val2][j][1]
                    j += 1
            while i < len1:
                dist += self.cate_cols[col][val1][i][1] * self.cate_cols[col][val1][i][1]
                i += 1
                cnt += 1
            while j < len2:
                dist += self.cate_cols[col][val2][j][1] * self.cate_cols[col][val2][j][1]
                j += 1
                cnt += 1
            return math.sqrt(dist / cnt)

    def __init__(self, df=[], aggr_col='count'):
        """Inits SampleClass with blah."""
        self.df = df
        self.cate_val_mark = {}
        self.cate_val_cnt = {}
        self.cate_val_list = {}
        self.cate_cols = {}
        self.dist_map = {}
        self.cos_sim_map = {}
        self.dist_stats = {}
        col_list = []
        for col in df:
            if col == 'index' or col == aggr_col:
                continue
            if df[col].dtype.kind == 'S' or df[col].dtype.kind == 'O':
                col_list.append(col)
                self.cate_val_mark[col] = {}
                self.cate_val_cnt[col] = 0
                self.cate_val_list[col] = []
                

        for idx, row in df.iterrows():
            for col in col_list:
                if row[col] not in self.cate_val_mark[col]:
                    self.cate_val_mark[col][row[col]] = self.cate_val_cnt[col]
                    self.cate_val_list[col].append(row[col])
                    self.cate_val_cnt[col] += 1

        for col in col_list:
            self.dist_map[col] = [[0.0 for i in range(self.cate_val_cnt[col])] for j in range(self.cate_val_cnt[col])]
            # self.cos_sim_map[col] = {}
            self.dist_stats[col] = {'max':0.0, 'min':1e10}

        print col_list
        print self.cate_val_list['pubkey']
        for col in df:
            if col == 'index' or col == 'name':
                continue
            if df[col].dtype.kind == 'S' or df[col].dtype.kind == 'O':
            #if is_string_dtype(df[col]):
                temp_col_list = col_list
                temp_col_list.remove(col)
                #print temp_col_list, col
                res = df.sort([col] + temp_col_list)
                self.cate_cols[col] = {}
                for idx, row in res.iterrows():
                    t = [map(lambda x: self.cate_val_mark[x][row[x]], temp_col_list), row[aggr_col]]
                    # for col2 in temp_col_list:
                    #     t[0].append(self.cate_val_mark[col2][row[col2]])
                    if not row[col] in self.cate_cols[col]:
                        #self.cate_cols[col][row[col]] = [(projection(row, temp_col_list), row[aggr_col])]
                        self.cate_cols[col][row[col]] = [t]
                    else:
                        #self.cate_cols[col][row[col]].append((projection(row, temp_col_list), row[aggr_col]))
                        if compare(t, self.cate_cols[col][row[col]][-1][0], aggr_col) != 0:
                            self.cate_cols[col][row[col]].append([t, row[aggr_col]])
                        else:
                            self.cate_cols[col][row[col]][-1][1] += row[aggr_col]
                temp_col_list.append(col)

        print self.cate_val_cnt
        for col in self.cate_cols:
            print col
            cnt = 0
            for val1 in self.cate_cols[col]:
                for val2 in self.cate_cols[col]:
                    id1 = self.cate_val_mark[col][val1]
                    id2 = self.cate_val_mark[col][val2]
                    cnt += 1
                    if val1 != val2:
                        self.dist_map[col][id1][id2] = self.__compute_distance(col, val1, val2, aggr_col)
                        if self.dist_map[col][id1][id2] > self.dist_stats[col]['max']:
                            self.dist_stats[col]['max'] = self.dist_map[col][id1][id2]
                        if self.dist_map[col][id1][id2] < self.dist_stats[col]['min']:
                            self.dist_stats[col]['min'] = self.dist_map[col][id1][id2]
                        # self.cos_sim_map[col][val1][val2] = self.__compute_cos_similarity(col, val1, val2, aggr_col)
                    else:
                        self.dist_map[col][id1][id2] = 0
                        # self.cos_sim_map[col][val1][val2] = 1.0

                    if cnt > 1000000:
                        cnt = 0
                        print col, val1, val2

            for val1 in self.cate_cols[col]:
                for val2 in self.cate_cols[col]:
                    if val1 != val2:
                        id1 = self.cate_val_mark[col][val1]
                        id2 = self.cate_val_mark[col][val2]
                        self.dist_map[col][id1][id2] -= 0.9 * self.dist_stats[col]['min']

    def compute_similarity(self, col, val1, val2, aggr_col):
        if col not in self.dist_map:
            return -1
        else:
            if val1 not in self.cate_val_mark[col] or val2 not in self.cate_val_mark[col]:
                return -1
            id1 = self.cate_val_mark[col][val1]
            id2 = self.cate_val_mark[col][val2]
            if val1 == val2:
                return 1.0
            else:
                
                return (1 - (self.dist_map[col][id1][id2]) 
                        / (self.dist_stats[col]['max']))
  
    def is_categorical(self, col):
        return col in self.cate_cols



    
