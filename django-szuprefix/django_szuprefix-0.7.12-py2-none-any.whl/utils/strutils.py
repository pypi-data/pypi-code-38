# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, division

import pandas as pd
import numpy as np

CHAR_DIGIT = 1
CHAR_ALPHA = 2
CHAR_CHINESE = 4


def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'


def is_alpha(char):
    return char.isalpha() and not is_chinese(char)


def is_digit(char):
    return char.isdigit()


def size(s):
    return len(s)


def digit_count(s):
    return sum([c.isdigit() for c in s])


def alpha_count(s):
    return sum([is_alpha(c) for c in s])


def chinese_count(s):
    return sum([is_chinese(c) for c in s])


def char_type(char):
    return is_digit(char) and CHAR_DIGIT \
           or is_chinese(char) and CHAR_CHINESE \
           or char.isalpha() and CHAR_ALPHA \
           or 0


def first_type(s):
    return char_type(s[0])


def last_type(s):
    return char_type(s[-1])


def first_code(s):
    return ord(s[0])


def last_code(s):
    return ord(s[-1])


def most_type(s):
    from collections import Counter
    ct = Counter()
    ct.update([char_type(c) for c in s])
    return ct.most_common(1)[0][0]


COMMON_CHINESE_XINGS = """李王张刘 陈杨赵黄 周吴徐孙 胡朱高林 何郭马罗
梁宋郑谢 韩唐冯于 董萧程曹 袁邓许傅 沈曾彭吕
苏卢蒋蔡 贾丁魏薛 叶阎余潘 杜戴夏钟 汪田任姜
范方石姚 谭廖邹熊 金陆郝孔 白崔康毛 邱秦江史
顾侯邵孟 龙万段雷 钱汤尹黎 易常武乔 贺赖龚文
庞樊兰殷 施陶洪翟 安颜倪严 牛温芦季 俞章鲁葛
伍韦申尤 毕聂丛焦 向柳邢路 岳齐沿梅 莫庄辛管
祝左涂谷 祁时舒耿 牟卜肖詹 关苗凌费 纪靳盛童
欧甄项曲 成游阳裴 席卫查屈 鲍位覃霍 翁隋植甘
景薄单包 司柏宁柯 阮桂闵欧阳 解强柴华 车冉房边
净阴闫佘 练骆付代 麦容悲初 瞿褚班全 名井米谈""".replace(' ', '')


def starts_with_chinese_xings(s):
    return s[0] in COMMON_CHINESE_XINGS


DIMENSION_FUNCTIONS = [
    size,
    first_code,
    first_type,
    last_code,
    last_type,
    most_type,
    digit_count,
    alpha_count,
    chinese_count
]

DIMENSION_FUNCTION_MAP = dict([(f.__name__, f) for f in DIMENSION_FUNCTIONS])


class DecisionTreeClassifier(object):
    def __init__(self, dimension_functions=DIMENSION_FUNCTIONS):
        from sklearn import tree
        self.tree = tree.DecisionTreeClassifier()
        self.dimension_functions = dimension_functions

    def train(self, names, categorys):
        X = [self.gen_dimention_vecter(n) for n in names]
        Y = categorys  # [t for o, t in data]
        self.tree.fit(X, Y)

    def predict(self, str_list, with_proba=False):
        X = [self.gen_dimention_vecter(s) for s in str_list]
        func = self.tree.predict_proba if with_proba else self.tree.predict
        return func(X)

    def gen_dimention_vecter(self, s):
        return [f(s) for f in self.dimension_functions]


class NNClassifier(object):
    def __init__(self, dimension_functions=DIMENSION_FUNCTIONS):
        self.model = self.create_nn_model()
        self.dimension_functions = dimension_functions

    def create_nn_model(self):
        import keras
        import tensorflow as tf
        return keras.Sequential([
            keras.layers.Dense(8, activation=tf.nn.relu),
            keras.layers.Dense(5, activation=tf.nn.softmax)
        ])

    def train(self, names, categorys):
        X = np.array([self.gen_dimention_vecter(n) for n in names])
        Y = np.array(categorys) / 100
        self.model.fit(X, Y, epochs=5)

    def predict(self, str_list):
        X = np.array([self.gen_dimention_vecter(s) for s in str_list])
        return self.model.predict(X)

    def normalize(self, n):
         return 0 if n == 0 else 1. / n

    def gen_dimention_vecter(self, s):
        return [self.normalize(f(s)) for f in self.dimension_functions]
