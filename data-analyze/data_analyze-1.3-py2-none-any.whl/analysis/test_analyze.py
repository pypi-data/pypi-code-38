# -*- coding: utf-8 -*-
# 测试结果分析
# chang.lu

from dataanalyze.rules.rules import test_rules
from dataanalyze.analysis.analyze_core import get_condition_match_result
from dataanalyze.analysis.analysis_result import AnalysisResult
from dataanalyze.utils.read_file import read_file_data


def test_log_analyze(test_data):
    """
    测试业务数据解析
    test_data 单条测试结果
    """
    analysis_result_list = list()
    analysis_result_object_list = list()
    for rule in test_rules:
        # 逐条遍历
        condition_result_list = list()
        for condition in rule.conditions:
            if condition.type == 'log':
                # 分析测试过程中系统日志
                log_data = read_file_data(test_data.logpath)
                condition_result = get_condition_match_result(condition, log_data)
                condition_result_list.append(condition_result)
            elif condition.type == 'assert':
                # 分析测试结果的assertmethod
                condition_result = get_condition_match_result(condition, test_data.assertMethodName)
                condition_result_list.append(condition_result)
            else:
                print('测试分析规则，不支持此类型', condition['type'])
        # condition 关系判断
        relation = rule.relation
        match_log = list()
        for c_ret in condition_result_list:
            relation = relation.replace(str(c_ret.id), str(c_ret.result))
            if c_ret.result_content:
                match_log.extend(c_ret.result_content)
        # 本条规则最终匹配结果
        result = eval(relation)
        print('规则: {} 匹配结果: {}'.format(rule.result.desc, result))
        analysis_result = AnalysisResult()
        analysis_result.caseName = test_data.caseName
        # 分析类型为test
        analysis_result.analysis_type = 'test'
        # 设置本次分析结果权重
        analysis_result.weights = rule.weights
        if result:
            # 根据规则匹配结果为True，则确认是bug
            analysis_result.is_confirm_bug = True
            # 问题分类 cloud/system
            analysis_result.type = rule.result.type
            # 问题模块
            analysis_result.module = rule.result.module
            # 问题描述
            analysis_result.desc = rule.result.desc
        else:
            analysis_result.is_confirm_bug = False
            # 问题分类 cloud/system
            analysis_result.type = 'system'
            # 问题模块
            analysis_result.module = test_data.module
            # 问题描述
            analysis_result.desc = test_data.assertMethodName
        analysis_result.extend.source_file_path = test_data.logpath
        # 根据条件匹配到的内容
        analysis_result.extend.log_info = match_log
        # 过滤重复结果
        #
        # analysis_result_list.append(analysis_result.toJson())
        analysis_result_object_list = filter_same_case(analysis_result, analysis_result_object_list)
    return analysis_result_list, analysis_result_object_list


def filter_same_case(analysis_result, analysis_result_list):
    """如果分析出的结果是在分析结果列表中，则进行数据合并
    合并逻辑：如果其中一个分析出原因，则采用此分析结果
    如果有多个分析结果，根据权重进行最终结果保留"""
    if analysis_result_list.__len__() == 0:
        analysis_result_list.append(analysis_result)
    else:
        for result in analysis_result_list:
            if analysis_result.caseName == result.caseName:
                if analysis_result.is_confirm_bug and result.is_confirm_bug:
                    # 都确认bug判断权重, 删除权重小的，保留权重大的
                    if analysis_result.weights > result.weights:
                        print(analysis_result.caseName, "更新")
                        analysis_result_list.remove(result)
                elif analysis_result.is_confirm_bug and not result.is_confirm_bug:
                    # 判断是否确认bug，删除未确认的，保留确认的
                    print(analysis_result.caseName, "更新")
                    analysis_result_list.remove(result)
                elif not analysis_result.is_confirm_bug and not result.is_confirm_bug:
                    # 都未确认bug，2个结果合并
                    pass
                analysis_result_list.append(analysis_result)
                break
    return analysis_result_list


