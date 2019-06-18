# -*- coding: utf-8 -*-
# 根据传入数据和规则进行结果分析
# chang.lu

import json
from dataanalyze.analysis.system_log_analyze import system_log_analyze
from dataanalyze.analysis.test_analyze import test_log_analyze
from dataanalyze.datas.test_result_data import load_test_result
from dataanalyze.analysis.analysis_result import StatisticalResults
from dataanalyze.utils.read_file import read_file_data


def data_analyze(analysis_type, data_type, data):
    """
    数据解析主入口
    type: file/data
    data: type=file,data文件路径; type=data, data=解析数据
    analysis_type: 对应规则类型 system，test，coredump
    """
    analysis_result_list = list()
    analysis_result_object_list = list()
    # 获取解析数据
    if data_type == 'file':
        data_content = read_file_data(data)
    elif data_type == 'data':
        pass
    else:
        print('不支持的数据类型', data_type)
        exit(1)
    if analysis_type == 'system':
        system_log_analyze(data_content)
    elif analysis_type == 'test':
        # 测试结果文件->测试结果类列表
        test_result_list = load_test_result(data_content)
        for test_result in test_result_list:
            if not test_result.status:  # 失败的用例进行分析
                analysis_result, analysis_result_object = test_log_analyze(test_result)
                analysis_result_list.extend(analysis_result)
                analysis_result_object_list.extend(analysis_result_object)
    elif analysis_type == 'coredump':
        pass
    else:
        print('不支持的分析类型', analysis_type)
    print(json.dumps(analysis_result_list))
    return analysis_result_object_list


def data_statistics(analysis_data):
    """对分析出的数据进行统计"""
    statistics_data_dict = dict()
    for one_data in analysis_data:
        caselist = dict()
        caselist['name'] = one_data.caseName
        caselist['log_path'] = one_data.extend.source_file_path
        key = one_data.type + one_data.module + one_data.desc
        if key in statistics_data_dict.keys():
            # 同一问题，total+1
            statistics_data_dict[key].total += 1
            statistics_data_dict[key].caselist.append(caselist)
        else:
            key = one_data.type + one_data.module + one_data.desc
            statistics_data = StatisticalResults()
            statistics_data.type = one_data.type
            statistics_data.module = one_data.module
            statistics_data.desc = one_data.desc
            statistics_data.is_confirm_bug = one_data.is_confirm_bug
            statistics_data.total = 1
            statistics_data.caselist.append(caselist)
            statistics_data_dict[key] = statistics_data
    result_list = list()
    result_object_list = list()
    for key, value in statistics_data_dict.items():
        result_list.append(value.toJson())
        result_object_list.append(value)
        print(json.dumps(result_list))
    return result_list, result_object_list


if __name__ == "__main__":
    result1 = data_analyze('test', 'file',
                           '/Users/yangcan/IdeaProjects/Tesla/originaldata/original_data_20190613120047')
    # analyzedata.AnalyzeData.saveFile(result1)
    (result2, result3) = data_statistics(result1)
    # analyzedata.AnalyzeData.saveFile(result2)
