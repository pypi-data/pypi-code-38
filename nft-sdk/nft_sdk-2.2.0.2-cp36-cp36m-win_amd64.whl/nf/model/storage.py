# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

import datetime

from nf.enum import MODE_BACKTEST

from nf.utils import load_to_list, ObjectLikeDict, timestamp2datetime, check_frequency
from nf.csdk.c_sdk import nfi_now
from nf.constant import DATA_TYPE_TICK


class DefaultFileModule(object):
    def on_tick(self, tick):
        print('please initialize method: on_tick')

    def on_bar(self, bars):
        print('please initialize method: on_bar')

    def on_bod(self, bod):
        print('please initialize method: on_bod')

    def on_eod(self, eod):
        print('please initialize method: on_eod')


class Context(object):
    __instance = None

    def __new__(cls, *args, **kwd):
        if Context.__instance is None:
            Context.__instance = object.__new__(cls, *args, **kwd)
            cls.strategy_id = ''
            cls.inside_file_module = DefaultFileModule()
            cls.token = None
            cls.mode = None
            cls.temporary_now = None
            cls.backtest_start_time = None
            cls.backtest_end_time = None
            cls.adjust_mode = None
            cls.inside_schedules = {}

        return Context.__instance

    def inside_init(self):
        self._bar_subs = []
        self._bar_tasks = []
        self._tick_subs = []
        self.inside_accounts = {}

    def inside_unsubscribe_all(self):
        self.inside_init()
        from nf.model.storage_data import SubBarData
        SubBarData().inside_init()

    def __init__(self):
        self._bar_subs = []
        self._bar_tasks = []
        self._tick_subs = []
        self.inside_accounts = {}

    @property
    def now(self):
        '''
        返回一个datetime对象
        '''
        if self.temporary_now:
            return self.temporary_now

        now = nfi_now()
        # now == 0 说明是回测模式而且处于init装填 c sdk拿不到时间
        if now == 0:
            return datetime.datetime.strptime(context.backtest_start_time, "%Y-%m-%d %H:%M:%S")

        return timestamp2datetime(now)

    def inside_append_bar_sub(self, sub):
        if not sub.unique:
            return
        # 添加sub
        self._bar_subs.append(sub)
        # 添加任务
        self._append_bar_task(sub)
        # contextdata 添加相关类实例
        from nf.model.storage_data import SubBarData
        SubBarData().sub_data(sub.sub_tag, sub.count)

    def inside_remove_bar_sub(self, sub):
        # 移除sub
        self._bar_subs.remove(sub)
        # 取消任务
        self._remove_bar_task(sub)
        # contextdata 去掉相关类实例
        from nf.model.storage_data import SubBarData
        SubBarData().unsub_data(sub.sub_tag)

    def inside_append_tick_sub(self, sub):
        if not sub.unique:
            return
        # 添加sub
        self._tick_subs.append(sub)

        # contextdata 添加相关类实例
        from nf.model.storage_data import SubTickData
        SubTickData().sub_data(sub.sub_tag, sub.count)

    def inside_remove_tick_sub(self, sub):
        # 移除sub
        self._tick_subs.remove(sub)

        # contextdata 去掉相关类实例
        from nf.model.storage_data import SubTickData
        SubTickData().unsub_data(sub.sub_tag)

    @property
    def symbols(self):
        """
        bar 的symbols + tick 的symbols
        """
        return set([sub.symbol for sub in self.inside_bar_subs]).union(self.inside_tick_subs)

    # @property
    # def parameters(self):
    #     """
    #     动态参数
    #     """
    #     from nf.api.basic import get_parameters
    #     parameters = get_parameters()
    #     return {p['key']: p for p in parameters}

    @property
    def inside_bar_subs(self):
        return self._bar_subs

    @property
    def inside_bar_tasks(self):
        return self._bar_tasks

    @property
    def inside_tick_subs(self):
        return self._tick_subs

    @staticmethod
    def data(symbol, frequency, count=1, fields=''):# 'symbol,bob,eob,open,high,low,close,volume'
        if fields:
            fields = load_to_list(fields)
        frequency = check_frequency(frequency)

        if DATA_TYPE_TICK == frequency:
            from nf.model.storage_data import SubTickData
            return SubTickData().get_data(symbol, frequency, count, fields)

        from nf.model.storage_data import SubBarData
        return SubBarData().get_data(symbol, frequency, count, fields)

    def _append_bar_task(self, sub):
        # 如果不是wait_group的直接当成一个单独的任务就行
        if not sub.wait_group:
            self._bar_tasks.append(BarTask(symbols=[sub.symbol], frequency=sub.frequency, wait_group=False, wait_group_timeout=sub.wait_group_timeout))
            return

        # 如果没有该频率的task，构建一个， 有的话， 对这个task成员进行添加
        if sub.frequency not in [task.frequency for task in self.inside_bar_tasks if task.wait_group == True]:
            self._bar_tasks.append(BarTask(symbols=[sub.symbol], frequency=sub.frequency, wait_group=True, wait_group_timeout=sub.wait_group_timeout))

        else:
            [task.symbols.add(sub.symbol) for task in self.inside_bar_tasks if sub.frequency == task.frequency and task.wait_group == True]

    def _remove_bar_task(self, sub):
        # 如果不是wait_group的， 说明都是单独订阅的
        if not sub.wait_group:
            [self._bar_tasks.remove(task) for task in self._bar_tasks if task.symbols == [sub.symbol] and not task.wait_group]
            return

        # 如果是wait_group的， 要判断是否是单独的
        [self._bar_tasks.remove(task) for task in self._bar_tasks if task.symbols == [sub.symbol] and task.wait_group]
        # task.symbols != [sub.symbol] 说明还有一起存的
        [task.symbols.remove(sub.symbol) for task in self._bar_tasks if sub.symbol in task.symbols and task.wait_group]


# 提供给API的唯一上下文实例
context = Context()
context.inside_init()


# 任务中心 按 symbols， frequency 来分组
class BarTask(object):
    def __init__(self, symbols, frequency, wait_group, wait_group_timeout):
        self.waiting = False
        self.symbols = set(symbols)
        self.frequency = frequency
        self.wait_group = wait_group
        self.overtime = wait_group_timeout

        self.performed_eobs = set()
        self.performed_bobs = set()
        self.wait_perform_eob = None
        self.wait_perform_bob = None
        self.newest_eob = None
        self.newest_bob = None
        self.count_dict = {}

    def set_wait_perform_eob(self, bar):
        symbol = bar['symbol']
        eob = bar['eob']
        frequency = bar['frequency']

        if symbol not in self.symbols or not frequency == self.frequency:
            return

        self.newest_eob = eob
        self.count_dict[eob] = self.count_dict.get(eob, 0) + 1
        if not self.wait_perform_eob and eob not in self.performed_eobs:
            self.wait_perform_eob = eob

    def set_wait_perform_bob(self, bar):
        symbol = bar['symbol']
        bob = bar['bob']
        frequency = bar['frequency']

        if symbol not in self.symbols or not frequency == self.frequency:
            return

        self.newest_bob = bob
        self.count_dict[bob] = self.count_dict.get(bob, 0) + 1
        if not self.wait_perform_bob and bob not in self.performed_bobs:
            self.wait_perform_bob = bob

    # 每接受一个数据， 都会判断下是否满足条件， 如果满足条件， 将is_ready 改成true
    def state_analysis_mode_live(self):
        # 执行过的任务不在执行
        if context.now + datetime.timedelta(seconds=-1 * int(self.frequency[0:-1])) in self.performed_bobs:
            print('state_analysis_mode_live: ', context.now + datetime.timedelta(seconds=-1 * int(self.frequency[0:-1])))
            print('now time: ', timestamp2datetime(nfi_now()))
            return

        if not self.wait_perform_bob:
            return

        # 要判断一下是不是订阅的代码都到了啊。
        if self.count_dict[self.wait_perform_bob] >= len(self.symbols):
            return self.sign_waiting()

        # 如果超时时间到了， 任务就必须执行
        if (context.now + datetime.timedelta(seconds=-1 * int(self.frequency[0:-1])) - self.wait_perform_bob).total_seconds() >= self.overtime:
            self.sign_waiting()
            return

    def state_analysis_mode_backtest(self):
        # 执行过的任务不在执行
        if context.now + datetime.timedelta(seconds=-1 * int(self.frequency[0:-1])) in self.performed_bobs:
            return

        if not self.wait_perform_bob:
            return

        # 要判断一下是不是订阅的代码都到了啊。
        if self.count_dict[self.wait_perform_bob] >= len(self.symbols):
            return self.sign_waiting()

        # 如果超时时间到了， 任务就必须执行, 而且还得修改下context.now
        if (context.now + datetime.timedelta(seconds=-1 * int(self.frequency[0:-1])) - self.wait_perform_bob).total_seconds() >= 2:
            context.temporary_now = self.wait_perform_bob
            self.sign_waiting()
            return

    # 任务执行以后要重置一下
    def reset(self):
        self.waiting = False
        self.performed_bobs.add(self.wait_perform_bob)

        if self.newest_bob == self.wait_perform_bob:
            self.wait_perform_bob = None
        else:
            self.wait_perform_bob = self.newest_bob

        # 回测的话 temorory_now 调回去
        if context.mode == MODE_BACKTEST:
            context.temporary_now = None

    # 标记待执行任务和状态
    def sign_waiting(self):
        self.waiting = True

    # 获取等待返回的bar
    def get_perform_bars(self):
        from nf.model.storage_data import SubBarData
        bars = SubBarData().inside_get_data(self.symbols, self.frequency, self.wait_perform_bob)
        bars = [ObjectLikeDict(bar) for bar in bars]
        return bars
