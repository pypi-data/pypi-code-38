#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import PUnittest, logger


class TestChat(PUnittest):
    """测试聊天功能"""

    def setUp(self):
        super(TestChat, self).setUp()
        logger.info("登录角色")

    def tearDown(self):
        logger.info("角色登出")
        super(TestChat, self).tearDown()

    @PUnittest.tag("Smoke", "Regression")
    @PUnittest.data(["哈哈", "此处超过字数上限"], [True, False])
    def test_chat(self, params, asserts):
        """测试在线聊天"""
        logger.info("登录另一个账号")
        logger.info("调用聊天接口，发送聊天信息 {}".format(params))
        result = True
        self.assertEqual(result, asserts)

    @PUnittest.tag("Smoke", "Regression")
    @PUnittest.data(["哈哈"], ["聊天对象不在线"])
    def test_msg(self, params, asserts):
        """测试留言"""
        logger.info("调用留言接口，发送留言信息 {}".format(params))
        result = "聊天对象不在线"
        self.assertIn(result, asserts)
