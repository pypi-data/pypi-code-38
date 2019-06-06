# -*- coding: utf-8 -*-
import random
from hashlib import md5
from .const import S, D, T, R, F


class GenString:

    def __init__(self, num, mode=None):
        """

        :param num: 需要生成几位随机字符串
        :param mode: 'S' -> 取自26个英文字母
                     'D’ -> 取自10个阿拉伯数字
                     'T' -> 取自 ""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""
                     'R' -> 取自 'S' + 'D'
                     'F' -> 取自 'S' + 'D' + 'R' + 'T'; 默认模式
        """
        self.num = num
        self.mode = mode

    def gen_random_string(self):
        if self.mode == 'R':
            mode = R
        elif self.mode == 'D':
            mode = D
        elif self.mode == 'S':
            mode = S
        elif self.mode == 'T':
            mode = T
        else:
            mode = F
        return ''.join(random.choice(mode) for i in range(self.num))


class GenSign:
    def __init__(self, data, key=None):
        """

        :param data: dict
        :param key: str
        """
        self.data = data
        self.key = key

    def create_sign(self):
        stringA = '&'.join(["{}={}".format(item, self.data.get(item)) for item in sorted(self.data)])
        stringSignTemp = stringA + "&key={}".format()
        if self.key:
            sign = md5(stringSignTemp.encode('utf-8')).hexdigest()
        else:
            sign = md5(stringA.encode('utf-8')).hexdigest()
        return sign.upper()
