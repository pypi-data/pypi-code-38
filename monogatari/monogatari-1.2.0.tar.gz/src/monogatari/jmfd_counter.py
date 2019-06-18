# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>
import os

from .dict_counter import DictCounter


class JMFDCounter(DictCounter):
    def __init__(self):
        path = os.path.dirname(__file__)
        super().__init__(f'{path}/data/J-MFD_2018.dic')
