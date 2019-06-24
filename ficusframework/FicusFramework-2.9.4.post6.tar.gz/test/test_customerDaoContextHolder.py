#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/2/25
import random
import threading
import time
from unittest import TestCase

from factdatasource.dao.FactDatasource import customer_dao_context_holder as holder


def run_1(num: str):
    """
    不同线程操作不用的num
    :param num:
    :return:
    """
    holder.set_source(num)
    print(f'{threading.current_thread().name}:set_{num}->{num}:{holder.get_source()}')
    print(f'{threading.current_thread().name}:set_{num}->True:{holder.is_using(num)}')
    holder.clear_source()
    print(f'{threading.current_thread().name}:clear_{num}->None:{holder.get_source()}')
    print(f'{threading.current_thread().name}:clear_{num}->False:{holder.is_using(num)}')


def run_2(num: str):
    """
    不同线程操作相同num
    :param num:
    :return:
    """
    time.sleep(random.random())
    holder.set_source(num)
    print(f'{threading.current_thread().name}:set_{num}->{num}:{holder.get_source()}')
    print(f'{threading.current_thread().name}:set_{num}->{holder.is_using(num)}->{holder.test()}')
    time.sleep(random.random())

    holder.clear_source()
    print(f'{threading.current_thread().name}:clear_{num}->None:{holder.get_source()}')
    print(f'{threading.current_thread().name}:clear_{num}->{holder.is_using(num)}->{holder.test()}')


class TestCustomerDaoContextHolder(TestCase):

    def test_holder_run_1(self):
        for i in range(0, 10):
            threading.Thread(target=run_1, name=f'线程{i}', args=(str(i),)).start()

    def test_holder_run_2(self):
        for i in range(0, 20):
            threading.Thread(target=run_2, name=f'线程{i}', args=('test',)).start()




