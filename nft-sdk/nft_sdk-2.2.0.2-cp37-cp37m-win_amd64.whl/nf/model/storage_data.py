# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

import pandas as pd

from collections import deque

from nf.constant import SUB_TAG, DATA_TYPE_TICK

from nf.model.storage import context


# 用来存储代码信息
class SubBarData(object):
    __instance = None

    def __new__(cls, *args, **kwd):
        if SubBarData.__instance is None:
            SubBarData.__instance = object.__new__(cls, *args, **kwd)
        return SubBarData.__instance

    def inside_init(self):
        self._data = {}

    def get_data(self, symbol, frequency, count, fields):
        sub_tag = SUB_TAG.format(symbol, frequency)
        if not self._data.get(sub_tag):
            return pd.DataFrame(columns=[fields])

        data = list(self._data[sub_tag].items)
        if not data:    # fill cache first
            self._data[sub_tag].data_init()
            data = list(self._data[sub_tag].items)
            if not data:    # if still no cache data
                return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(data)
        if fields:
            return data[fields].tail(count)
        else:
            return data.tail(count)

    def inside_get_data(self, symbols, frequency, bob):
        data = [self._inside_get_data(symbol, frequency, bob) for symbol in symbols]
        data = [info for info in data if info]
        return data

    def _inside_get_data(self, symbol, frequency, bob):
        sub_tag = SUB_TAG.format(symbol, frequency)
        if not self._data.get(sub_tag):
            return

        data = list(self._data[sub_tag].items)
        data.reverse()

        # 看看能否获取bar
        for bar in data:
            if bar['bob'] == bob:
                return bar

    def set_data(self, bar):
        if not isinstance(bar, dict):
            raise ValueError('set_data 应该传入的是dict类型')

        sub_tag = SUB_TAG.format(bar['symbol'], bar['frequency'])
        single_bar_storage = self._data.get(sub_tag)
        # 有些时候取消订阅了，也推送bar过来了， 这里做个容错处理
        if single_bar_storage is None:
            return

        # 回测时滑窗为0的时候， 尝试进行数据填充
        # if context.mode == MODE_BACKTEST and not single_bar_storage.items:
        #     single_bar_storage.data_init()

        # 如果滑窗缓存队列中没有数据， 尝试进行数据填充
        if not single_bar_storage.items:
            single_bar_storage.data_init()

        single_bar_storage.enqueue(bar)

    @property
    def largest_count(self):
        sub_list = [{'sub_name': sub.sub_tag, 'count': sub.count} for sub in context.inside_bar_subs]
        sub_list.sort(key=lambda obj: obj.get('count'), reverse=False)
        return {sub['sub_name']: sub['count'] for sub in sub_list}

    # 用户订阅数据后， contextdata应该初始化一个SubInfoQueue
    def sub_data(self, sub_tag, count):
        single_bar_storage = self._data.get(sub_tag)
        if not single_bar_storage:
            self._data[sub_tag] = BarInfoQueue(sub_tag, count)
            # 实时模式下, 数据填充放在订阅后
            # if context.mode == MODE_LIVE:
            #     self._data[sub_tag].data_init()
            return

        sub_info_queue = self._data.get(sub_tag)
        if sub_info_queue.count <= count:
            self._data[sub_tag] = BarInfoQueue(sub_tag, count)
            # 实时模式下, 数据填充放在订阅后
            # if context.mode == MODE_LIVE:
            #     self._data[sub_tag].data_init()
            return

    # 取消订阅直接清空就行了
    def unsub_data(self, sub_tag):
        if not self._data.get(sub_tag):
            return
        self._data.pop(sub_tag)


# 固定大小的先进先出队列
class BarInfoQueue(object):

    def __init__(self, sub_tag, count):
        self.sub_id = sub_tag
        self.count = count
        self.items = deque(maxlen=count)

    def enqueue(self, item):
        """进队列"""
        eobs = [i['eob'] for i in self.items]
        if item['eob'] not in eobs:
            self.items.append(item)

    def data_init(self):
        now = context.now.strftime("%Y-%m-%d %H:%M:%S")
        pre, symbol, frequency = self.sub_id.split(':')

        from nf.api import history_n

    #    if context.mode == MODE_BACKTEST:
    #        adjust_end_time = context.backtest_end_time
    #    else:
    #        adjust_end_time = ''

        datas = history_n(symbol, frequency, self.count, end_time=now)

    #    if frequency == '1d':
    #        for data in datas:
    #            data['eob'] = data['eob'].replace(hour=15, minute=15, second=1)

        [self.enqueue(data) for data in datas]


SubBarData().inside_init()


# 用来存储代码信息
class SubTickData(object):
    __instance = None

    def __new__(cls, *args, **kwd):
        if SubTickData.__instance is None:
            SubTickData.__instance = object.__new__(cls, *args, **kwd)
        return SubTickData.__instance

    def inside_init(self):
        self._data = {}

    def get_data(self, symbol, frequency, count, fields):
        sub_tag = SUB_TAG.format(symbol, frequency)
        if not self._data.get(sub_tag):
            return pd.DataFrame(columns=[fields])

        data = list(self._data[sub_tag].items)
        if not data:    # fill cache first
            self._data[sub_tag].data_init()
            data = list(self._data[sub_tag].items)
            if not data:  # if still no cache data
                return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(data)

        if fields:
            return data[fields].tail(count)
        else:
            return data.tail(count)

    def inside_get_data(self, symbols, frequency, created_at):
        data = [self._inside_get_data(symbol, frequency, created_at) for symbol in symbols]
        data = [info for info in data if info]
        return data

    def _inside_get_data(self, symbol, frequency, created_at):
        sub_tag = SUB_TAG.format(symbol, frequency)
        if not self._data.get(sub_tag):
            return

        data = list(self._data[sub_tag].items)
        data.reverse()

        # 看看能否获取数据
        for bar in data:
            if bar['created_at'] == created_at:
                return bar

    def set_data(self, tick):
        if not isinstance(tick, dict):
            print('type of input is : ', type(tick))
            raise ValueError('set_data 应该传入的是dict类型')

        sub_tag = SUB_TAG.format(tick['symbol'], DATA_TYPE_TICK)
        single_data_storage = self._data.get(sub_tag)
        # 有些时候取消订阅了，也推送过来了， 这里做个容错处理
        if single_data_storage is None:
            return

        # 回测时滑窗为0的时候， 尝试进行数据填充
        # if context.mode == MODE_BACKTEST and not single_data_storage.items:
        #     single_data_storage.data_init()

        # 如果滑窗缓存队列中没有数据， 尝试进行数据填充
        if not single_data_storage.items:
            single_data_storage.data_init()

        single_data_storage.enqueue(tick)

    @property
    def largest_count(self):
        sub_list = [{'sub_name': sub.sub_tag, 'count': sub.count} for sub in context.inside_tick_subs]
        sub_list.sort(key=lambda obj: obj.get('count'), reverse=False)
        return {sub['sub_name']: sub['count'] for sub in sub_list}

    # 用户订阅数据后， contextdata应该初始化一个SubInfoQueue
    def sub_data(self, sub_tag, count):
        single_data_storage = self._data.get(sub_tag)
        if not single_data_storage:
            self._data[sub_tag] = TickInfoQueue(sub_tag, count)
            # 实时模式下, 数据填充放在订阅后
            # if context.mode == MODE_LIVE:
            #     self._data[sub_tag].data_init()
            return

        sub_info_queue = self._data.get(sub_tag)
        if sub_info_queue.count <= count:
            self._data[sub_tag] = TickInfoQueue(sub_tag, count)
            # 实时模式下, 数据填充放在订阅后
            # if context.mode == MODE_LIVE:
            #     self._data[sub_tag].data_init()
            return

    # 取消订阅直接清空就行了
    def unsub_data(self, sub_tag):
        if not self._data.get(sub_tag):
            return
        self._data.pop(sub_tag)


# 固定大小的先进先出队列
class TickInfoQueue(object):

    def __init__(self, sub_tag, count):
        self.sub_id = sub_tag
        self.count = count
        self.items = deque(maxlen=count)

    def enqueue(self, item):
        """进队列"""
        eobs = [i['created_at'] for i in self.items]
        if item['created_at'] not in eobs:
            self.items.append(item)

    def data_init(self):
        now = context.now.strftime("%Y-%m-%d %H:%M:%S")
        pre, symbol, frequency = self.sub_id.split(':')

        from nf.api import history_n

    #    if context.mode == MODE_BACKTEST:
    #        adjust_end_time = context.backtest_end_time
    #    else:
    #        adjust_end_time = ''

        datas = history_n(symbol, frequency, self.count, end_time=now)

        [self.enqueue(data) for data in datas]


SubTickData().inside_init()
