# -*- coding: utf-8 -*-
# 分析结果
# chang.lu

import json

class TestResult:
    def __init__(self, json=None):
        self.castName = ''
        self.module = ''
        self.assertMethodName = ''
        self.status = True
        self.deviceTypeId = ''
        self.imageVersion = ''
        self.sn = ''
        self.logpath = ''


def load_test_result(data):
    data = json.loads(data)
    data_list = list()
    for test_result in data:
        test_result_object = TestResult()
        test_result_object.__dict__ = test_result
        data_list.append(test_result_object)
    return data_list

