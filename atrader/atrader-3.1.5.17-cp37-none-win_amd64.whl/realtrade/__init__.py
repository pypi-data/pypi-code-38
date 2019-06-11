# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 11:35:15 2018

@author: kunlin.l
"""

# noinspection PyUnresolvedReferences
from atrader import enums
from collections import Iterable
# noinspection PyUnresolvedReferences
from atrader.tframe import sysclsbase as cnt
# noinspection PyUnresolvedReferences
from atrader.tframe.sysclsbase import smm
# noinspection PyUnresolvedReferences
from atrader.tframe.sysclsbase import gv
# noinspection PyUnresolvedReferences
from atrader.tframe.utils.argchecker import apply_rule, verify_that
from atrader.tframe.udefs import ONE_YEAR_AGO
from atrader.tframe.ufuncs import convert_str_or_datetime_to_int_date

__all__ = [
    'run_realtrade',
]


@smm.force_mode(gv.RUNMODE_CONSOLE)
@smm.force_phase(gv.RUMMODE_PHASE_DEFAULT)
@apply_rule(verify_that('strategy_name').is_instance_of(str),
            verify_that('account_list').is_instance_of(tuple, list),
            verify_that('target_list').is_instance_of(Iterable),
            verify_that('frequency').is_valid_frequency(),
            verify_that('fre_num').is_instance_of(int).is_greater_than(0),
            verify_that('begin_date').is_valid_date(),
            verify_that('fq').is_in((enums.FQ_BACKWARD,
                                     enums.FQ_FORWARD,
                                     enums.FQ_NA)))
def run_realtrade(strategy_name='',
                  file_path='.',
                  account_list=(),
                  target_list=(),
                  frequency='min',
                  fre_num=1,
                  begin_date=ONE_YEAR_AGO,
                  fq=enums.FQ_NA, **kwargs):
    if isinstance(begin_date, str) and begin_date.strip() == '':
        begin_date = ONE_YEAR_AGO

    config = {
        'entry': {
            'strategy_name': strategy_name,
            'strategy_path': file_path,
            'accounts': account_list,
            'targets': list(target_list),
            'frequency': frequency,
            'freq_num': fre_num,
            'begin_date': convert_str_or_datetime_to_int_date(begin_date),
            'fq': fq
        },
        'extra': kwargs,
    }

    from .main import main_run_real_trade
    return main_run_real_trade(config)
