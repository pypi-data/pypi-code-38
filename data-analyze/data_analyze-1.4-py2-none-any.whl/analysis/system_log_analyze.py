# -*- coding: utf-8 -*-
# 系统日志分析
# chang.lu

from dataanalyze.rules.rules import system_rules
from dataanalyze.analysis.analyze_core import get_condition_match_result
from dataanalyze.analysis.analysis_result import AnalysisResult


def system_log_analyze(data):
  """系统日志进行解析"""
  for rule in system_rules:
    # 规则逐条遍历
    condition_result_list = list()
    for condition in rule.conditions:
      if condition.type == 'log':
        condition_result = get_condition_match_result(condition, data)
        condition_result_list.append(condition_result)
      else:
        print('系统分析规则，不支持此类型', condition['type'])
    # condition 关系判断
    relation = rule.relation
    for c_ret in condition_result_list:
      relation = relation.replace(str(c_ret.id), str(c_ret.result))
    # 本条规则最终匹配结果
    result = eval(relation)
    print('规则: {} 匹配结果: {}'.format(rule.result.desc, result))
    analysis_result = AnalysisResult()
    analysis_result.module = rule.result.module
    analysis_result.desc = rule.result.desc




