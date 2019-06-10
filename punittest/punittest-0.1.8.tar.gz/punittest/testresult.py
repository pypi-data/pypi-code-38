#! /usr/bin/env python
# -*- coding: UTF-8 -*-

from .utils.logger import logger
import time
import io
import sys
import unittest


class TestResult(unittest.TestResult):
    def __init__(self, verbosity=1):
        super().__init__(verbosity)
        # 根据report的log开关取不同的值
        if logger.log_capture is None:
            self.outputBuffer = io.StringIO()
        else:
            self.outputBuffer = logger.log_capture
        self.raw_stdout = None
        self.raw_stderr = None
        self.success_count = 0
        self.failure_count = 0
        self.skip_count = 0
        self.error_count = 0
        self.verbosity = verbosity
        self.result = []
        self._case_start_time = 0
        self._case_run_time = 0

    def startTest(self, test):
        self._case_start_time = time.time()
        super().startTest(test)
        # 将StringIO重定向到sys.stdout
        self.raw_stdout = sys.stdout
        self.raw_stderr = sys.stderr
        sys.stdout = self.outputBuffer
        sys.stderr = self.outputBuffer

    def complete_output(self):
        self._case_run_time = time.time() - self._case_start_time
        if self.raw_stdout:
            sys.stdout = self.raw_stdout
            sys.stderr = self.raw_stderr
        # 从StringIO中读取log信息
        result = self.outputBuffer.getvalue()
        lines = result.splitlines()
        # 移除每条测试用例的开始和结束标记，只留下内容
        start_idx, end_idx = 0, 0
        for i, line in enumerate(lines):
            if "* Start *" in line:
                start_idx = i
            elif "* End *" in line:
                end_idx = i
        if end_idx > start_idx:
            result = '\n'.join(lines[start_idx + 1: end_idx])
            result += '\n'
        # 移动StringIO的偏移指针，读取新的IO内容
        self.outputBuffer.seek(0)
        self.outputBuffer.truncate()
        return result

    def stopTest(self, test):
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        super().addSuccess(test)
        output = self.complete_output()
        self.result.append((0, test, output, '', self._case_run_time))

    def addError(self, test, err):
        self.error_count += 1
        super().addError(test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str, self._case_run_time))
        logger.error("Load TestCase Error:")
        logger.error(_exc_str)

    def addSkip(self, test, reason):
        self.skip_count += 1
        super().addSkip(test, reason)
        self.result.append((3, test, "", "", 0.0))

    def addFailure(self, test, err):
        self.failure_count += 1
        super().addFailure(test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str, self._case_run_time))
        logger.error("Load TestCase Failed:")
        logger.error(_exc_str)
