# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import
import six

from nf.api import PositionSide_Long, PositionSide_Short


# 账户
class Account(object):
    def __init__(self, id, name, cash, positions):
        self.id = id
        self.name = name
        self.cash = cash
        self.inside_positions = positions

    def match(self, name):
        if self.name == name:
            return True

        if self.id == name:
            return True

    def positions(self, symbol='', side=None):
        # 默认返回全部
        if not symbol and not side:
            info = list(six.itervalues(self.inside_positions))
            return info

        # 只有side 返回空仓和多仓
        if not symbol and side:
            info = list(six.itervalues(self.inside_positions))
            return [i for i in info if i.get('side') == side]

        # 只有symbol 没有side 返回固定symbol的空仓和多仓
        if symbol and not side:
            long_key = '{}.{}'.format(symbol, PositionSide_Long)
            long_info = self.inside_positions.get(long_key)

            short_key = '{}.{}'.format(symbol, PositionSide_Short)
            short_info = self.inside_positions.get(short_key)

            result = []
            if long_info:
                result.append(long_info)
            if short_info:
                result.append(short_info)
            return result

        # 返回指定仓位
        key = '{}.{}'.format(symbol, side)
        info = self.inside_positions.get(key)
        if not info:
            return []

        return [info]

    def position(self, symbol, side):
        key = '{}.{}'.format(symbol, side)
        return self.inside_positions.get(key)
