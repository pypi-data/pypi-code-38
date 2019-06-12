#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/03/30 12:10
# @Author  : niuliangtao
# @Site    :
# @File    : data.py
# @Software: PyCharm

import json

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from ..utils import data_root
from ..utils import download_file
from ..utils import raw_root


def get_adult_data():
    train_path = data_root + "/data/adult.data.txt"
    test_path = data_root + "/data/adult.test.txt"

    download_file(url=raw_root + "/recommendation/data/adult.data.txt", path=train_path)
    download_file(url=raw_root + "/recommendation/data/adult.test.txt", path=test_path)

    train_data = pd.read_table(train_path, header=None, delimiter=',')
    test_data = pd.read_table(test_path, header=None, delimiter=',')

    all_columns = ['age', 'workclass', 'fnlwgt', 'education', 'education-num',
                   'marital-status', 'occupation', 'relationship', 'race', 'sex',
                   'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'label', 'type']

    continus_columns = ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
    dummy_columns = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'sex',
                     'native-country']

    train_data['type'] = 1
    test_data['type'] = 2

    all_data = pd.concat([train_data, test_data], axis=0)
    all_data.columns = all_columns

    all_data = pd.get_dummies(all_data, columns=dummy_columns)

    test_data = all_data[all_data['type'] == 2].drop(['type'], axis=1)
    train_data = all_data[all_data['type'] == 1].drop(['type'], axis=1)

    train_data['label'] = train_data['label'].map(lambda x: 1 if x.strip() == '>50K' else 0)
    test_data['label'] = test_data['label'].map(lambda x: 1 if x.strip() == '>50K.' else 0)

    for col in continus_columns:
        ss = StandardScaler()
        train_data[col] = ss.fit_transform(train_data[[col]].astype(np.float64))
        test_data[col] = ss.transform(test_data[[col]].astype(np.float64))

    train_y = train_data['label']
    train_x = train_data.drop(['label'], axis=1)
    test_y = test_data['label']
    test_x = test_data.drop(['label'], axis=1)

    return train_x, train_y, test_x, test_y


def get_porto_seguro_data():
    train_path = data_root + "/data/porto_seguro_train.csv"
    test_path = data_root + "/data/porto_seguro_test.csv"

    download_file(url=raw_root + "/recommendation/data/porto_seguro_train.csv", path=train_path)
    download_file(url=raw_root + "/recommendation/data/porto_seguro_test.csv", path=test_path)

    # https://links.jianshu.com/go?to=https%3A%2F%2Fwww.kaggle.com%2Fc%2Fporto-seguro-safe-driver-prediction


def get_bitly_usagov_data():
    file_path = data_root + "/data/bitly_usagov.txt"

    download_file(url=raw_root + "/recommendation/data/adult.data.txt", path=file_path)

    s1 = open(file_path).read()

    s2 = []
    for s in s1.split("\n"):
        try:
            s2.append(json.loads(s))
        except Exception as e:
            pass

    return pd.DataFrame.from_dict(s2)
