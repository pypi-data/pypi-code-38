#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .settings import Settings
from .utils.parse_excel import ExcelParser
from .utils.logger import logger
from importlib import import_module
import unittest
import re


class TestSet:
    """读取测试用例表格中的数据，生成PUnittest可识别的测试用例对象"""
    def __init__(self, filter_hidden=True):
        """
        :param filter_hidden: 过滤被隐藏的excel
        """
        self._excel = ExcelParser(Settings.TEST_EXCEL_PATH, 'TestCases')
        self.tags = Settings.RUN_TAGS
        self.excel_cases = self._get_excel_cases(True)
        self.test_suite = None

    @staticmethod
    def _convert_params(params):
        """将测试用例中的ParamsData由字符串转换成python数据结构"""
        if params is None:
            return None
        elif isinstance(params, bool):
            return [params]
        else:
            param_list = params.split('\n')
            try:
                param_list = [eval(x.strip()) for x in param_list]
            except NameError:
                param_list = [x.strip() for x in param_list]
            return param_list

    @staticmethod
    def _convert_asserts(asserts):
        """将测试用例中的AssertResult由字符串转换成python数据结构"""
        if asserts is None:
            return None
        elif isinstance(asserts, bool):
            return [asserts]
        else:
            asserts_list = asserts.split('\n')
            try:
                asserts_list = [eval(x.strip()) for x in asserts_list]
            except NameError:
                asserts_list = [x.strip() for x in asserts_list]
            return asserts_list

    @staticmethod
    def _convert_tags(tags):
        """将测试用例中的Tag解析成列表"""
        tag_list = ['All']
        if tags is None:
            return tag_list
        elif isinstance(tags, list):
            tag_list.extend(tags)
            return tag_list
        else:
            tag_list.extend(tags.split('\n'))
            tag_list = [x.strip() for x in tag_list]
            return tag_list

    def _get_excel_cases(self, filter_hidden):
        """
        一次性读取所有测试用例
        :param filter_hidden: bool, 是否过滤excel中被隐藏的行
        :return: [dict(case), dict(case)...]形式的suite
        """
        test_set = list()
        titles = [x for x in self._excel.get_row_values(1)]
        for row in range(2, self._excel.max_row + 1):
            test_case = dict()
            # 获取该行是否被隐藏
            row_hidden = self._excel.worksheet.row_dimensions[row].hidden
            if filter_hidden is False or (filter_hidden is True and row_hidden is False):
                values = [x for x in self._excel.get_row_values(row)]
                if len(values) < len(titles):
                    for i in range(len(titles) - len(values)):
                        values.append(None)
                for idx, (title, value) in enumerate(zip(titles, values)):
                    if title == 'ParamsData':
                        params = self._convert_params(value)
                        test_case[title] = params
                    elif title == 'AssertResult':
                        asserts = self._convert_asserts(value)
                        test_case[title] = asserts
                    elif title == 'Tags':
                        tags = self._convert_tags(value)
                        test_case[title] = tags
                    else:
                        test_case[title] = value
                test_set.append(test_case)
        self._test_set = test_set
        return test_set

    def filter_test_case(self, **titles):
        """
        根据表格中的title过滤测试用例
        :param titles: 关键字参数，每个参数名对应表格中的title
        :return: 测试用例组成的列表
        """
        test_case = self.test_set
        if titles:
            for title, value in titles.items():
                test_case = list(filter(lambda d: title in d.keys(), test_case))
                test_case = list(filter(lambda d: d[title] == value, test_case))
        return test_case

    def make_test_suite(self):
        """
        将excel表格中读取的测试用例生成 PUnittest 能识别的 TestSuite 对象，或者获取本地的所有测试文件
        :return: unittest.TestSuite 对象
        """
        test_suite = unittest.TestSuite()
        # 从Excel中读取测试用例
        if Settings.EXCEL_TEST_SET:
            if len(self.excel_cases) > 0:
                for test_case in self.excel_cases:
                    _dir_name = test_case['TestDir'] if 'TestDir' in test_case else None
                    _file_name = test_case['TestFile'] if 'TestFile' in test_case else None
                    _cls_name = test_case['TestClass'] if 'TestClass' in test_case else None
                    _case_name = test_case['TestCase'] if 'TestCase' in test_case else None
                    try:
                        package = import_module('{0}.{1}'.format(_dir_name, _file_name))
                        cls = getattr(package, _cls_name)
                        for name, func in list(cls.__dict__.items()):
                            _name = re.sub(r'_#[\d]*', '', name)
                            _name = re.sub(r'test_\d{5}', 'test', _name)
                            if _name == _case_name:
                                case = cls(name)
                                test_suite.addTest(case)
                    except Exception as e:
                        logger.error('Fail to load test case <{0}><{1}>: {2}'.format(_cls_name, _case_name, e))
            else:
                logger.error('Fail to load any test case, please check')
                raise RuntimeError('Fail to load any test case, please check')
        # 从TestSuite文件夹中读取所有测试用例
        else:
            test_suite.addTests(unittest.TestLoader().discover(Settings.TEST_SUITE_DIR))
        self.test_suite = test_suite
        return test_suite


if __name__ == '__main__':
    t = TestSet()
    suite = t.make_test_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
