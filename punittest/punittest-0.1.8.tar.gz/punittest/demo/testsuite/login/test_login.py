#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import PUnittest, logger


class TestLogin(PUnittest):
    """测试登录功能"""

    @PUnittest.tag("Smoke", "Regression")
    @PUnittest.data([{'user': 'username', 'pass': 'password'}], [True])
    def test_login_successfully(self, params, asserts):
        """测试登录成功"""
        _user, _passwd = params['user'], params['pass']
        _result = asserts
        logger.info("调用登录接口，用户名/密码: {}/{}， 获取登录结果".format(_user, _passwd))
        result = True
        self.assertTrue(_result, result)

    @PUnittest.tag("Regression")
    @PUnittest.data(
        [{'user': 'username', 'pass': '123'},
         {'user': '123', 'pass': 'password'},
         {'user': '', 'pass': ''}],
        [False, False, False])
    def test_login_failed(self, params, asserts):
        """测试登录失败"""
        _user, _passwd = params['user'], params['pass']
        _result = asserts
        logger.info("调用登录接口，用户名/密码: {}/{}， 获取登录结果".format(_user, _passwd))
        result = False
        self.assertTrue(_result, result)

    @PUnittest.skip("这里跳过不测")
    @PUnittest.tag("Regression")
    @PUnittest.data([{'user': 'username', 'pass': 'password'}], [True])
    def test_relogin_successfully(self, params, asserts):
        """测试重新登录成功"""
        _user, _passwd = params['user'], params['pass']
        _result = asserts
        logger.info("调用登录接口，用户名/密码: {}/{}， 获取登录结果".format(_user, _passwd))
        result = True
        self.assertTrue(_result, result)
        logger.info("调用登录接口，用户名/密码: {}/{}， 获取登录结果".format(_user, _passwd))
        result = True
        self.assertTrue(_result, result)
