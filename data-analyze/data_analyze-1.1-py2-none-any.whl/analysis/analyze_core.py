# -*- coding: utf-8 -*-
# 核心解析规则，根据正则表达式 或 确定字符进行匹配
# chang.lu

import re
from dataanalyze.analysis.analysis_result import ConditionResult


def condition_match(regx, data):
    """
    条件匹配
    返回结果 true/false
    """
    match_flag = False
    match_list = list()
    prog = re.compile(regx)
    for line in str(data).split('\n'):
        ret = prog.finditer(line)
        if ret:
            for tx in ret:
                match_flag = True
                match_list.append(tx.group())
                print('匹配到规则【', regx, '】内容 ', tx.group())
    return match_flag, match_list


def get_condition_match_result(condition, log_data):
    # 分析结果，result = 是否匹配成功，match_list = 匹配的内容list
    result, match_list = condition_match(condition.condition, log_data)
    # 组装 condition
    condition_result = ConditionResult()
    condition_result.id = condition.id
    condition_result.result = result
    if match_list:
        condition_result.result_content = match_list
    condition_result.condition = condition.condition
    return condition_result
