#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/06/05 10:34
# @Author  : niuliangtao
# @Site    : 
# @File    : ElectronicsData.py
# @Software: PyCharm
import os
import pickle
import random

import numpy as np
import pandas as pd

from ..utils import data_root
from ..utils import download_file


class ElectronicsData:
    def __init__(self):
        # 源文件保存目录
        self.path_root = data_root + "/data/electronics/"

        # 源文件
        self.json_meta = self.path_root + '/meta_Electronics.json'
        self.json_reviews = self.path_root + '/reviews_Electronics_5.json'

        # 格式化文件
        self.pkl_meta = self.path_root + '/raw_data/meta.pkl'
        self.pkl_reviews = self.path_root + '/raw_data/reviews.pkl'

        # 结果文件
        self.pkl_remap = self.path_root + '/raw_data/remap.pkl'
        self.pkl_dataset = self.path_root + '/raw_data/dataset.pkl'

    def download_raw_0(self):
        download_file(
            url="http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Electronics_5.json.gz",
            path=self.json_reviews)

        download_file(
            url="http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Electronics.json.gz",
            path=self.json_meta)

        cmd1 = 'cd ' + self.path_root + ' && gzip -d reviews_Electronics_5.json.gz'
        cmd2 = 'cd ' + self.path_root + ' && gzip -d meta_Electronics.json.gz'

        print(os.system(cmd1))
        print(os.system(cmd2))

    def convert_pd_1(self):
        def to_df(file_path):
            with open(file_path, 'r') as fin:
                df = {}
                i = 0
                for line in fin:
                    df[i] = eval(line)
                    i += 1
                df = pd.DataFrame.from_dict(df, orient='index')
                return df

        reviews_df = to_df(self.json_reviews)
        with open(self.pkl_reviews, 'wb') as f:
            pickle.dump(reviews_df, f, pickle.HIGHEST_PROTOCOL)

        meta_df = to_df(self.json_meta)
        meta_df = meta_df[meta_df['asin'].isin(reviews_df['asin'].unique())]
        meta_df = meta_df.reset_index(drop=True)
        with open(self.pkl_meta, 'wb') as f:
            pickle.dump(meta_df, f, pickle.HIGHEST_PROTOCOL)

    def remap_id_2(self):
        random.seed(1234)

        with open(self.pkl_reviews, 'rb') as f:
            reviews_df = pickle.load(f)
            reviews_df = reviews_df[['reviewerID', 'asin', 'unixReviewTime']]
        with open(self.pkl_meta, 'rb') as f:
            meta_df = pickle.load(f)
            meta_df = meta_df[['asin', 'categories']]
            meta_df['categories'] = meta_df['categories'].map(lambda x: x[-1][-1])

        def build_map(df, col_name):
            key = sorted(df[col_name].unique().tolist())
            m = dict(zip(key, range(len(key))))
            df[col_name] = df[col_name].map(lambda x: m[x])
            return m, key

        asin_map, asin_key = build_map(meta_df, 'asin')
        cate_map, cate_key = build_map(meta_df, 'categories')
        revi_map, revi_key = build_map(reviews_df, 'reviewerID')

        user_count, item_count, cate_count, example_count = \
            len(revi_map), len(asin_map), len(cate_map), reviews_df.shape[0]
        print('user_count: %d\t item_count: %d\t cate_count: %d\t example_count: %d' %
              (user_count, item_count, cate_count, example_count))

        meta_df = meta_df.sort_values('asin')
        meta_df = meta_df.reset_index(drop=True)
        reviews_df['asin'] = reviews_df['asin'].map(lambda x: asin_map[x])
        reviews_df = reviews_df.sort_values(['reviewerID', 'unixReviewTime'])
        reviews_df = reviews_df.reset_index(drop=True)
        reviews_df = reviews_df[['reviewerID', 'asin', 'unixReviewTime']]

        cate_list = [meta_df['categories'][i] for i in range(len(asin_map))]
        cate_list = np.array(cate_list, dtype=np.int32)

        with open(self.pkl_remap, 'wb') as f:
            pickle.dump(reviews_df, f, pickle.HIGHEST_PROTOCOL)  # uid, iid
            pickle.dump(cate_list, f, pickle.HIGHEST_PROTOCOL)  # cid of iid line
            pickle.dump((user_count, item_count, cate_count, example_count),
                        f, pickle.HIGHEST_PROTOCOL)
            pickle.dump((asin_key, cate_key, revi_key), f, pickle.HIGHEST_PROTOCOL)

    def init_data(self):
        self.download_raw_0()

        self.convert_pd_1()

        self.remap_id_2()

    def build_dataset(self):
        random.seed(1234)

        with open(self.pkl_remap, 'rb') as f:
            reviews_df = pickle.load(f)
            cate_list = pickle.load(f)
            user_count, item_count, cate_count, example_count = pickle.load(f)

        train_set = []
        test_set = []
        for reviewerID, hist in reviews_df.groupby('reviewerID'):
            pos_list = hist['asin'].tolist()

            def gen_neg():
                neg = pos_list[0]
                while neg in pos_list:
                    neg = random.randint(0, item_count - 1)
                return neg

            neg_list = []
            for i in range(len(pos_list)):
                neg_list.append(gen_neg())

            for i in range(1, len(pos_list)):
                hist = pos_list[:i]
                if i != len(pos_list) - 1:
                    train_set.append((reviewerID, hist, pos_list[i], 1))
                    train_set.append((reviewerID, hist, neg_list[i], 0))
                else:
                    label = (pos_list[i], neg_list[i])
                    test_set.append((reviewerID, hist, label))

        random.shuffle(train_set)
        random.shuffle(test_set)

        assert len(test_set) == user_count
        # assert(len(test_set) + len(train_set) // 2 == reviews_df.shape[0])

        with open(self.pkl_dataset, 'wb') as f:
            pickle.dump(train_set, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(test_set, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(cate_list, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump((user_count, item_count, cate_count), f, pickle.HIGHEST_PROTOCOL)
