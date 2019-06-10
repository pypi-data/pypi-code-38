#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import SETTINGS, RELOAD_SETTINGS
# 先修改punittest的设置然后重载
SETTINGS.EXCEL_TEST_SET = True
SETTINGS.RUN_TAGS = ["All"]
SETTINGS.LOG_FILE_SWITCH = True
SETTINGS.LOG_REPORT_SWITCH = True
SETTINGS.LOG_DIR = r"D:\Temp\Logs"
SETTINGS.REPORT_DIR = r"D:\Temp\Reports"
RELOAD_SETTINGS()


from punittest import PUnittest
# 如果有需要在这里为Punittest添加类属性，
# 供测试类和测试用例继承
PUnittest.placeholder = None


from punittest import TestRunner
# 运行测试
runner = TestRunner("demo接口测试用例")
runner.run()
