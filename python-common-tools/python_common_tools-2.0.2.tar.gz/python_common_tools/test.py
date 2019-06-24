# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-04-25 10:58'

import os
import shutil
import time
import unittest

from python_common_tools.cache import cache_function, cache_daily_function
from python_common_tools.linux import get_bash_output, get_latest_commit_id
from python_common_tools.log import setup_logger
from python_common_tools.network import secure_requests, secure_requests_json
from python_common_tools.parallel import run_func_parallel
import logging


class TestLog(unittest.TestCase):

    def test_nofile_log(self):
        logger = setup_logger()
        logger.info("log info test")
        logger.error("log error test")

    def test_log_file(self):
        logger = setup_logger("test.log")
        logger.info("log info test")
        logger.error("log error test")
        with open("test.log") as f:
            s = f.read()
            # logger.info(f"The length of the logger file is {len(s)}")
            self.assertGreater(len(s), 0)
        os.remove("test.log")


class TestNetwork(unittest.TestCase):

    def setUp(self) -> None:
        self.logger = logging.getLogger("python_common_tools.test")

    def test_secure_get_json(self):
        url = 'https://m.douban.com/j/puppy/frodo_landing?include=anony_home'
        j = secure_requests_json(url)
        self.logger.info(j)
        self.assertIsNotNone(j)

    def test_secure_get(self):
        url = 'https://www.baidu.com/'
        r = secure_requests(url)
        self.logger.info(r.status_code)


@cache_function('.')
def f(a, b, c):
    time.sleep(3)
    return a + b + c


@cache_daily_function('.')
def f2(a, b, c):
    time.sleep(3)
    return a + b + c


class TestCache(unittest.TestCase):

    @cache_function('.', is_method=True)
    def f(self, a, b, c):
        time.sleep(3)
        return a + b + c

    @cache_daily_function('.', is_method=True)
    def f2(self, a, b, c):
        time.sleep(3)
        return a + b + c

    def test_cache_function(self):
        begin = time.time()
        r1 = f(1, 2, 3)
        end = time.time()
        t1 = end - begin
        begin = time.time()

        r2 = f(1, 2, 3)
        shutil.rmtree("f")
        end = time.time()
        t2 = end - begin
        self.assertEqual(r1, 6)
        self.assertEqual(r2, 6)
        self.assertGreater(t1, t2)
        self.assertAlmostEqual(t1, 3.0, places=0)
        self.assertNotAlmostEqual(t2, 3.0, places=0)

        begin = time.time()
        r1 = self.f(1, 2, 3)
        end = time.time()
        t1 = end - begin
        begin = time.time()

        r2 = self.f(1, 2, 3)
        shutil.rmtree("TestCache.f")
        end = time.time()
        t2 = end - begin
        self.assertEqual(r1, 6)
        self.assertEqual(r2, 6)
        self.assertGreater(t1, t2)
        self.assertAlmostEqual(t1, 3.0, places=0)
        self.assertNotAlmostEqual(t2, 3.0, places=0)

    def test_cache_daily_function(self):
        begin = time.time()
        r1 = self.f2(1, 2, 3)
        end = time.time()
        t1 = end - begin
        begin = time.time()

        r2 = self.f2(1, 2, 3)
        shutil.rmtree("TestCache.f2")
        end = time.time()
        t2 = end - begin
        self.assertEqual(r1, 6)
        self.assertEqual(r2, 6)
        self.assertGreater(t1, t2)
        self.assertAlmostEqual(t1, 3.0, places=0)
        self.assertNotAlmostEqual(t2, 3.0, places=0)


class TestLinux(unittest.TestCase):

    def test_get_bash_output(self):
        output = get_bash_output(["echo", "hello"])
        self.assertEqual(output, "hello\n")

    def test_get_latest_commit_id(self):
        output = get_latest_commit_id()
        self.assertEqual(len(output.strip()), 40)

    def test_open_remote_file(self):
        pass


def test_func1(i):
    return i


def test_func2(i, j):
    return i * j


def test_callback_func(i, r, callback_func_extra_kwargs):
    logger = callback_func_extra_kwargs["logger"]
    logger.info(f"i={i},r={r}")


class TestRunFuncParallel(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("python_common_tools.test")

    def test_run_func_parallel(self):
        func_args_list1 = list(range(10))
        callback_func_extra_kwargs = {"logger": self.logger}
        self.logger.info("test func with one single param in thread style")
        run_func_parallel(test_func1, func_args_list1, test_callback_func, callback_func_extra_kwargs)

        self.logger.info("test func with one single param in process style")
        run_func_parallel(test_func1, func_args_list1, test_callback_func, callback_func_extra_kwargs, style="process")

        func_args_list2 = [(i, i) for i in range(10)]
        self.logger.info("test func with one more param in thread style")
        run_func_parallel(test_func2, func_args_list2, test_callback_func, callback_func_extra_kwargs)

        self.logger.info("test func with one more param in process style")
        run_func_parallel(test_func2, func_args_list2, test_callback_func, callback_func_extra_kwargs, style="process")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
