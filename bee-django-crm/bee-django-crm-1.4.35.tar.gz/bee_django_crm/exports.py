#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
from utils import get_now
from .models import Poster, PreUserContract, PreUserFee
from .signals import fee_checked

__author__ = 'zhangyue'


# 获取显示的海报<poster_id>列表
# 生成的海报路径为：/<CRM_POSTER_PHOTO_PATH>/<poster_id>/<user_id>_poster.jpg
def get_poster_show_list():
    posters = Poster.objects.filter(is_show=True)
    show_list = []
    for poster in posters:
        show_list.append(poster.id)
    return show_list


# 随机获取海报id
def get_random_poster_id():
    posters = get_poster_show_list()
    if len(posters) == 0:
        return None
    poster_id = random.choice(posters)
    return poster_id


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


# 费用审核后续操作
def after_check_callback(preuser_fee_id, user=None, new_user=False):
    try:
        preuser_fee = PreUserFee.objects.get(id=preuser_fee_id)
        preuser_fee.after_checked_at = get_now()
        preuser_fee.save()
        # 审核后发送信号
        fee_checked.send(sender=PreUserContract, preuser_fee=preuser_fee, user=user, new_user=new_user)
        return True, None
    except Exception as e:
        return False, e.__str__()


# 获取合同的天数
# return month/week,<时长>
def get_peruser_contract_days(preuser_contract_id):
    try:
        peruser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        contract = peruser_contract.contract
        return contract.period, contract.duration
    except:
        return None, None


# 获取合同的开始日期
# 弃用
def get_peruser_contract_start_day(preuser_contract_id):
    try:
        peruser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        return peruser_contract.study_at
    except:
        return None


# 获取合同的开始日期和结束日期
def get_peruser_contract_start_finish_date(preuser_contract_id):
    try:
        peruser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        return peruser_contract.study_at, peruser_contract.finish_at
    except:
        return None, None


# 获取缴费时的开始日期，及付款方式
# return month/week,<时长>
# 弃用
def get_peruser_fee_start_day(preuser_fee_id):
    try:
        peruser_fee = PreUserFee.objects.get(id=preuser_fee_id)
        return peruser_fee.study_at, peruser_fee.pay_status
    except:
        return None
