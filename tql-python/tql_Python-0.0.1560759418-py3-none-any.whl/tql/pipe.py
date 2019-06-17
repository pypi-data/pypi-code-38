#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'iter'
__author__ = 'JieYuan'
__mtime__ = '18-12-14'
"""

from .utils.xx import xx
from .eda import DataFrameSummary
from .utils import cprint

try:
    from IPython import get_ipython

    if 'IPKernelApp' not in get_ipython().config:
        raise ImportError("console")
except:
    from tqdm import tqdm

else:
    from tqdm import tqdm_notebook as tqdm

import warnings

warnings.filterwarnings("ignore")
#########################################################################
import os
import re
import time
import json
import pickle
import socket
import inspect
import joblib
import requests
import numpy as np
import pandas as pd
import jieba
import jieba.analyse as ja

from pathlib import Path
from functools import reduce
from contextlib import contextmanager
from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import *
from sklearn.linear_model import *
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.feature_extraction.text import TfidfVectorizer

#########################################################################


# p = Path(__file__)
get_module_path = lambda path, file=__file__: \
    os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(file), path))


###################################################################

def pd_set():
    """
    pd.set_option('display.max_rows', 1024)
    pd.set_option('display.max_columns', 128)
    pd.set_option('max_colwidth', 128)  # 列宽
    # pd.set_option('expand_frame_repr', False)  # 允许换行显示
    """
    pd.set_option('display.max_rows', 1024)
    pd.set_option('display.max_columns', 128)
    pd.set_option('max_colwidth', 128)  # 列宽
    # pd.set_option('expand_frame_repr', False)  # 允许换行显示
    print('Setting Success!')


import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")  # darkgrid, whitegrid, dark, white,和ticks
sns.set_context('paper')


# sns.plotting_context()
# sns.axes_style()


# plt.style.use('ggplot')

def plot_set():
    """
    plt.rcParams['font.sans-serif'] = ['Simhei']  # 中文乱码的处理
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False  # 负号
    plt.rcParams["text.usetex"] = False
    plt.rcParams["legend.numpoints"] = 1
    plt.rcParams["figure.figsize"] = (18, 9)  # (12, 6)
    plt.rcParams["figure.dpi"] = 128
    plt.rcParams["savefig.dpi"] = plt.rcParams["figure.dpi"]
    plt.rcParams["font.size"] = 12
    plt.rcParams["pdf.fonttype"] = 42
    """
    plt.rcParams['font.sans-serif'] = ['Simhei']  # 中文乱码的处理
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False  # 负号
    plt.rcParams["text.usetex"] = False
    plt.rcParams["legend.numpoints"] = 1
    plt.rcParams["figure.figsize"] = (18, 9)  # (12, 6)
    plt.rcParams["figure.dpi"] = 128
    plt.rcParams["savefig.dpi"] = plt.rcParams["figure.dpi"]
    plt.rcParams["font.size"] = 12
    plt.rcParams["pdf.fonttype"] = 42
    print('Setting Success!')


#########################################################################


# 序列化
# df.to_hdf('./data.h5', 'w', complib='blosc', complevel=8)
def reader(fname='./tmp.txt', sep=',', mode='r'):
    with open(fname, mode) as f:
        for l in f:
            yield l.strip().split(sep)


@xx
def xwrite(iterable, fname, mode='w', glue='\n'):
    with open(fname, mode) as f:
        for item in iterable:
            f.write(str(item) + glue)


@xx
def xpickle_dump(obj, file='tmp.pkl'):
    with open(file, 'wb') as f:
        pickle.dump(obj, f)


@xx
def xpickle_load(file):
    with open(file, 'rb') as f:
        return pickle.load(f)


# 统计函数: 待补充groupby.agg
xsummary = xx(lambda iterable: DataFrameSummary(list(iterable) | xDataframe)['iterable'])
xvalue_counts = xx(
    lambda iterable, normalize=False, bins=None: pd.value_counts(list(iterable), normalize=normalize, bins=bins))

__funcs = [sum, min, max, abs, len, np.mean, np.median]
xsum, xmin, xmax, xabs, xlen, xmean, xmedian = [xx(i) for i in __funcs]

xnorm = xx(lambda iterable, ord=2: np.linalg.norm(iterable, ord))
xl1 = xx(lambda iterable: np.linalg.norm(iterable, 1))
xl2 = xx(lambda iterable: np.linalg.norm(iterable, 2))

xcount = xx(lambda iterable: Counter(list(iterable)))

xunique = xx(lambda iterable: list(OrderedDict.fromkeys(list(iterable))))  # 移除列表中的重复元素(保持有序)
xsort = xx(lambda iterable, reverse=False, key=None: sorted(list(iterable), key=key, reverse=reverse))

xmax_index = xx(lambda x: max(range(len(x)), key=x.__getitem__))  # 列表中最小和最大值的索引
xmin_index = xx(lambda x: min(range(len(x)), key=x.__getitem__))  # 列表中最小和最大值的索引
xmost_freq = xx(lambda x: max(set(x), key=x.count))  # 查找列表中频率最高的值, key作用于set(x), 可类推出其他用法


# print
@xx
def xprint(obj, mode=None, bg='blue'):
    if mode:
        for i in obj:
            cprint(i)
            print('\n')
    else:
        cprint(obj, bg)


xtqdm = xx(lambda iterable, desc=None: tqdm(iterable, desc))

# base types
xtuple, xlist, xset = xx(tuple), xx(list), xx(set)

# string
xjoin = xx(lambda s, sep=' ': sep.join(s))
xcut = xx(lambda s, cut_all=False: jieba.lcut(s, cut_all=cut_all))
xtfidf = xx(lambda s, topK=20: ja.tfidf(s, topK=topK))

# list transform
xgroup_by_step = xx(lambda ls, step=3: [ls[idx: idx + step] for idx in range(0, len(ls), step)])


# dict
@xx
def xjson(dict_):
    _ = json.dumps(dict_, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
    return _


@xx
def xSeries(iterable, name='iterable'):
    if isinstance(iterable, pd.Series):
        return iterable
    else:
        return pd.Series(iterable, name=name)


@xx
def xDataframe(iterable, name='iterable'):
    if isinstance(iterable, pd.DataFrame):
        return iterable
    else:
        return pd.DataFrame({name: iterable})


# 高阶函数
xmap = xx(lambda iterable, func: map(func, iterable))
xreduce = xx(lambda iterable, func: reduce(func, iterable))
xfilter = xx(lambda iterable, func: filter(func, iterable))


# multiple
@xx
def xThreadPoolExecutor(iterable, func, max_workers=5):
    """
    with ThreadPoolExecutor(max_workers) as pool:
        pool.map(func, iterable)
    """
    with ThreadPoolExecutor(max_workers) as pool:
        return pool.map(func, iterable)


@xx
def xProcessPoolExecutor(iterable, func, max_workers=5):
    """
    with ProcessPoolExecutor(max_workers) as pool:
        pool.map(func, iterable)
    """
    with ProcessPoolExecutor(max_workers) as pool:
        return pool.map(func, iterable)


# host
hostname = socket.getfqdn(socket.gethostname())
localhost = socket.gethostbyname(hostname)

# args
get_args = lambda func: inspect.getfullargspec(func).args


@contextmanager
def timer(task_name="timer"):
    # a timer cm from https://www.kaggle.com/lopuhin/mercari-golf-0-3875-cv-in-75-loc-1900-s
    print('\n')
    cprint(">>> {} started".format(task_name))
    t0 = time.time()
    yield
    cprint(">>> {} done in {:.0f} seconds".format(task_name, time.time() - t0))
