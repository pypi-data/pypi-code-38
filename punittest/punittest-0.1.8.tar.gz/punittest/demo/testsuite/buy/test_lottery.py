#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import PUnittest, logger


class TestLottery(PUnittest):
    """测试游戏内抽奖功能"""

    def setUp(self):
        super(TestLottery, self).setUp()
        logger.info("登录角色")
        logger.info("修改角色货币")

    def tearDown(self):
        logger.info("角色登出")
        super(TestLottery, self).tearDown()

    @PUnittest.tag("Smoke", "Regression")
    def test_lottery_successfully(self):
        """测试抽奖成功"""
        logger.info("调用抽奖接口，获取抽奖结果")
        result = ["抽奖道具列表"]
        self.assertIn("抽奖道具列表", result)

    @PUnittest.tag("Smoke", "Regression")
    def test_lottery_not_enough_gold(self):
        """测试抽奖货币不足"""
        logger.info("将角色货币归0")
        logger.info("调用抽奖接口，获取抽奖结果")
        result = "货币不足"
        self.assertIn("抽奖道具列表", result)

    @PUnittest.tag("Regression")
    def test_lottery_cost(self):
        """测试抽奖花费"""
        logger.info("调用抽奖接口，获取抽奖结果")
        result = 100
        self.assertIn(result, 100)
