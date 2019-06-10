#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


class Settings:

    _root = os.path.abspath(os.path.dirname(__file__))
    _base = os.path.abspath(os.path.dirname(_root))
    
    # 是否被外部修改
    __SPECIFIED__ = False

    # 日志文件存放的目录
    LOG_DIR = os.path.join(_base, "logs")
    # 报告文件存放的目录
    REPORT_DIR = os.path.join(_base, "reports")
    # 需要执行测试用例（python文件）的目录地址
    TEST_SUITE_DIR = os.path.join(_root, 'demo', 'testsuite')
    # 需要执行测试用例（excel文件）的地址
    TEST_EXCEL_PATH = os.path.join(_root, "excel_testset", "TestCases.xlsx")

    # 过滤日志的级别
    LOG_CONSOLE_LEVEL = "DEBUG"
    LOG_FILE_LEVEL = "DEBUG"
    LOG_REPORT_LEVEL = "DEBUG"

    # 是否开启日志的开关
    LOG_CONSOLE_SWITCH = True
    LOG_FILE_SWITCH = False
    LOG_REPORT_SWITCH = False

    # 测试用例执行次数（>=1 则失败后会重新执行）
    CASE_FAIL_RERUN = 1
    # 是否从Excel表格中读取测试用例
    EXCEL_TEST_SET = False
    # 执行包含如下Tags的测试用例
    RUN_TAGS = ["All"]
