# -*- coding: utf-8 -*-
# 分析结果
# chang.lu

class AnalysisResult():

    def __init__(self):
        self.analysis_type = '' # 分析类型
        self.is_confirm_bug = False
        self.caseName = '' # 测试标签
        self.type = '' # 问题类型
        self.module = '' # 问题模块
        self.desc = '' # 问题描述
        self.weights = 0
        self.extend = AnalysisResultExtend()

    def toJson(self):
        json_obj = dict()
        json_obj['analysis_type'] = self.analysis_type
        json_obj['is_confirm_bug'] = self.is_confirm_bug
        json_obj['caseName'] = self.caseName
        json_obj['type'] = self.type
        json_obj['module'] = self.module
        json_obj['desc'] = self.desc
        json_obj['extend'] = self.extend.__dict__
        return json_obj

class AnalysisResultExtend:
    def __init__(self):
        self.source_file_path = '' # 数据源文件
        self.log_info = '' # 分析匹配到的日志

class ConditionResult:

    def __init__(self):
        self.id = 0
        self.condition = ''  # 匹配条件
        self.result = '' # True/False 是否满足条件
        self.result_content = list() # 匹配内容
        self.weights = 0

class StatisticalResults:
    def __init__(self):
        self.is_confirm_bug = False # 标识是否分析出问题
        self.desc = ''
        self.type = ''
        self.module = ''
        self.total = 0
        self.originaldatapath = ''
        self.caselist = list()

    def toJson(self):
        json_object = dict()
        json_object['is_confirm_bug'] = self.is_confirm_bug
        json_object['desc'] = self.desc
        json_object['type'] = self.type
        json_object['module'] = self.module
        json_object['total'] = self.total
        json_object['originaldatapath'] = self.originaldatapath
        json_object['caselist'] = self.caselist
        return json_object





