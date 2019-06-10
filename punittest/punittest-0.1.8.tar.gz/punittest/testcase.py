#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from .settings import Settings
from .testset import TestSet
from .utils.logger import logger
from functools import wraps
import unittest
import sys

CASE_TAG_FLAG = "__case_tag__"
CASE_DATA_FLAG = "__case_data__"
CASE_ID_FLAG = "__case_id__"
CASE_INFO_FLAG = "__case_info__"
CASE_RUN_INDEX_FlAG = "__case_run_index_flag__"
CASE_SKIP_FLAG = "__unittest_skip__"
CASE_SKIP_REASON_FLAG = "__unittest_skip_why__"


def skip(reason):
    def wrap(func):
        return unittest.skip(reason)(func)
    return wrap


def skip_if(condition, reason):
    def wrap(func):
        return unittest.skipIf(condition, reason)(func)
    return wrap


def data(params, asserts):
    """注入测试数据，可以做为测试用例的数据驱动
    :param params: 测试数据组成的list
    :param asserts: 断言数据组成的list
    :return:
    """
    def wrap(func):
        param_data = {'params': params, 'asserts': asserts}
        setattr(func, CASE_DATA_FLAG, param_data)
        return func
    return wrap


def tag(*tag_type):
    """指定测试用例的标签，可以作为测试用例分组使用，用例默认会有Tag.ALL标签，支持同时设定多个标签，如：
    @tag(Tag.V1_0_0, Tag.SMOKE)
    def test_func(self):
        pass

    :param tag_type:标签类型，在tag.py里边自定义
    :return:
    """
    def wrap(func):
        if not hasattr(func, CASE_TAG_FLAG):
            tags = {'All'}
            tags.update(tag_type)
            setattr(func, CASE_TAG_FLAG, tags)
        else:
            getattr(func, CASE_TAG_FLAG).update(tag_type)
        return func
    return wrap


def _assertion(func):
    """用来装饰PUnittest类中所有的AssertXxx方法，提供日志，
    并且当出现断言异常不会立即终止用例，而是等用例结束后抛出所有的断言异常"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info('[Assert]: {0}{1}'.format(func.__name__, format(args[1:])))
            return func(*args, **kwargs)
        except AssertionError as e:
            args[0].Exc_Stack.append(e)
    return wrapper


def _handler(rerun=Settings.CASE_FAIL_RERUN):
    """处理测试用例，为用例添加格式化的日志。并提供失败重跑机制。"""
    def wrapper(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            _testcase_name = args[0]._testMethodName
            _testcase_doc = args[0]._testMethodDoc
            _testclass_name = args[0].__class__.__name__
            _testclass_doc = args[0].__class__.__doc__
            rerun_time = rerun
            while rerun_time > 0:
                try:
                    logger.info('[TestCase]: {0}.{1} {2}|{3}'.format(
                        _testclass_name, _testcase_name, _testclass_doc, _testcase_doc))
                    logger.info('[TestProgress]: {0}/{1} [RerunTime]: NO.{2}'.format(
                        getattr(func, CASE_RUN_INDEX_FlAG), TestCaseHandler.actual_case_num, rerun - rerun_time + 1))
                    args[0]._clear_exc_stack()
                    result = func(*args, **kwargs)
                    # 用例执行完毕抛出所有可能存在的AssertionError异常
                    args[0]._raise_exc()
                    logger.info('[TestResult]: Pass!')
                    return result
                except AssertionError as e:
                    rerun_time -= 1
                    if rerun_time <= 0:
                        logger.error('[TestResult]: Fail!')
                        raise e
                except Exception as e:
                    rerun_time -= 1
                    if rerun_time <= 0:
                        _, _, exc_traceback = sys.exc_info()
                        logger.error('[TestResult]: Error!')
                        raise e
        return wrap
    return wrapper


def _feed_data(*args, **kwargs):
    def wrap(func):
        @wraps(func)
        def _wrap(self):
            return func(self, *args, **kwargs)
        return _wrap
    return wrap


class TestCaseHandler:
    actual_case_num = 0
    total_case_num = 0

    @classmethod
    def create_case_id(cls):
        cls.total_case_num += 1
        return cls.total_case_num

    @classmethod
    def create_actual_run_index(cls):
        cls.actual_case_num += 1
        return cls.actual_case_num

    @staticmethod
    def modify_func_name(func, index):
        """修改函数名字，实现排序，并且根据DDT数据的编号在函数名后添加编号 eg test_fight >> test_00001_fight_#1
        :param func:
        :param index:
        :return:
        """
        case_id = TestCaseHandler.create_case_id()
        setattr(func, CASE_ID_FLAG, case_id)
        func_name = func.__name__.replace("test_", "test_{:05d}_".format(case_id))
        if index is not None:
            func_name += "_#{0}".format(index)
        return func_name

    @staticmethod
    def create_case_with_case_data(func):
        """根据原有测试函数创建新的带参数的测试函数"""
        result = dict()
        test_data = getattr(func, CASE_DATA_FLAG)
        params = test_data['params']
        asserts = test_data['asserts']
        for index, (param, assert_) in enumerate(zip(params, asserts), 1):
            if not hasattr(func, CASE_SKIP_FLAG):
                setattr(func, CASE_RUN_INDEX_FlAG, TestCaseHandler.create_actual_run_index())
            func_name = TestCaseHandler.modify_func_name(func, index)
            result[func_name] = _handler()(_feed_data(params=param, asserts=assert_)(func))
        return result

    @staticmethod
    def create_case_without_case_data(func):
        """根据原有测试函数创建新的不带参数的测试函数"""
        result = dict()
        if not hasattr(func, CASE_SKIP_FLAG):
            setattr(func, CASE_RUN_INDEX_FlAG, TestCaseHandler.create_actual_run_index())
        func_name = TestCaseHandler.modify_func_name(func, None)
        result[func_name] = _handler()(func)
        return result

    @staticmethod
    def classify_funcs(funcs_dict):
        """将类中的函数进行归类"""
        funcs = dict()
        cases = dict()
        asserts = dict()
        for attr in funcs_dict:
            if attr.startswith("test_"):
                cases[attr] = funcs_dict[attr]
            elif attr.startswith("assert"):
                asserts[attr] = funcs_dict[attr]
            else:
                funcs[attr] = funcs_dict[attr]
        return funcs, cases, asserts

    @staticmethod
    def filter_cases_by_tags(tags, func):
        """根据func的tags进行过滤"""
        name = func.__name__
        if name.startswith('test_'):
            _tags = getattr(func, CASE_TAG_FLAG, {'All'})
            for _tag in _tags:
                if _tag in tags:
                    break
            else:
                msg = "不包含需要执行的Tag: {}".format(', '.join(tags))
                filtered_func = skip(msg)(func)
                return filtered_func
        return func


class Meta(type):
    def __new__(mcs, cls_name, supers, cls_dict):
        testset = TestSet()
        sets = testset.excel_cases
        tags = testset.tags
        funcs, cases, asserts = TestCaseHandler.classify_funcs(cls_dict)
        for name, assert_ in asserts.items():
            # 将装饰过的assert方法加入类
            funcs.update({name: _assertion(assert_)})

        # 读取Excel中的数据为测试函数绑定装饰器
        if Settings.EXCEL_TEST_SET:
            for test_case in sets:
                _cls_name = test_case['TestClass'] if 'TestClass' in test_case else None
                _case_name = test_case['TestCase'] if 'TestCase' in test_case else None
                _case_desc = test_case['CaseDescription'] if 'CaseDescription' in test_case else None
                _tags = test_case['Tags'] if 'Tags' in test_case else None
                _skip = test_case['Skip'] if 'Skip' in test_case else None
                _params = test_case['ParamsData'] if 'ParamsData' in test_case else None
                _asserts = test_case['AssertResult'] if 'AssertResult' in test_case else None
                if cls_name == _cls_name:
                    for test_func in cases.values():
                        if test_func.__name__ == _case_name:
                            # 为测试函数绑定tag装饰器
                            test_func = tag(*_tags)(test_func)
                            # 根据tag进行过滤
                            test_func = TestCaseHandler.filter_cases_by_tags(tags, test_func)
                            # 为测试函数绑定skip装饰器，excel和硬编码任何一个有skip则跳过
                            skip_ = getattr(test_func, CASE_SKIP_FLAG, None)
                            if not skip_ and _skip:
                                test_func = skip(_skip)(test_func)
                            # 修改测试函数的文档注释
                            if _case_desc:
                                setattr(test_func, '__doc__', _case_desc)
                            # 为测试函数绑定data装饰器
                            if _asserts is not None and _params is not None:
                                test_func = data(_params, _asserts)(test_func)
                                funcs.update(TestCaseHandler.create_case_with_case_data(test_func))
                            else:
                                funcs.update(TestCaseHandler.create_case_without_case_data(test_func))

        # 根据测试函数硬编码为测试函数绑定装饰器
        else:
            for test_func in cases.values():
                # if not hasattr(test_func, CASE_TAG_FLAG):
                #     setattr(test_func, CASE_TAG_FLAG, 'All')  # 没有指定tag的用例，默认带有tag：ALL
                # 根据tag进行过滤
                test_func = TestCaseHandler.filter_cases_by_tags(tags, test_func)
                # 注入用例信息
                case_info = "{}.{}".format(test_func.__module__, test_func.__name__)
                setattr(test_func, CASE_INFO_FLAG, case_info)
                # 注入测试数据
                if hasattr(test_func, CASE_DATA_FLAG):
                    funcs.update(TestCaseHandler.create_case_with_case_data(test_func))
                else:
                    funcs.update(TestCaseHandler.create_case_without_case_data(test_func))

        return super(Meta, mcs).__new__(mcs, cls_name, supers, funcs)
